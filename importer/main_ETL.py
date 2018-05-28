"""
MAIN ETL Pipeline

#REFACTOR: module needs refactoring.

Module executes the import pipeline:
    - Download raw data sources from objectstore, guided by the sources.conf file.
    - Store this data in a local data directory.
    - Parse the raw data and write the results to postgresql database (in Docker container).
"""

import logging
import configparser
import argparse
import os
import os.path
import re

import download_from_objectstore
import objectstore
import parsers
from ETLFunctions import DatabaseInteractions
from ETLFunctions import ModifyTables
from ETLFunctions import LoadLayers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

db_int = DatabaseInteractions()
conn = db_int.get_sqlalchemy_connection()


# TODO Use this structure to refactor the main function
def execute_download_from_objectstore():
    """This function downloads data for all ENABLED containers in importer/sources.conf from the objectstore."""
    objectstore_containers = [config_src.get(x, 'OBJSTORE_CONTAINER') for x in datasets]

    # Check whether locally cached downloads should be used.
    ENV_VAR = 'EXTERNAL_DATASERVICES_USE_LOCAL'
    use_local = True if os.environ.get(ENV_VAR, '') == 'TRUE' else False

    if not use_local:
        if not LOCAL_DATA_DIRECTORY:
            raise ValueError("data dir missing")
        download_from_objectstore.main(objectstore_containers, LOCAL_DATA_DIRECTORY)
    else:
        logger.info('No download from datastore requested, quitting.')

    rename_quantillion_dump()


def load_areas():
    """Load 'stadsdeel' and 'buurtcombinatie' tables into database."""
    pg_str = db_int.get_postgresql_string()
    LoadLayers.load_layers(pg_str)


def parse_and_write():
    """This function parses the data downloaded from the objectstore and writes it to the database (Docker container)"""

    # Remove dependent tables created by the Analyzer (only necessary when developing locally)
    drop_query = """
    DROP TABLE IF EXISTS public.datasets_buurtcombinatiedrukteindex;
    DROP TABLE IF EXISTS public.datasets_hotspotsdrukteindex;
    """
    conn.execute(drop_query)

    # Parse raw data from objectstore and place result into database (in Docker container).
    for dataset in datasets:
        logger.info(f'Parsing and writing {dataset} data...')

        # if statement below is needed because alpha's parser writes
        # directly to database, whereas other parsers
        # return a dataframe. #TODO refactor?
        if dataset == 'alpha':
            getattr(parsers, 'parse_' + dataset)(
                datadir=LOCAL_DATA_DIRECTORY)

        else:
            df = getattr(parsers, 'parse_' + dataset)(
                    datadir=LOCAL_DATA_DIRECTORY)
            df.to_sql(
                name=config_src.get(dataset, 'TABLE_NAME'),
                con=conn, index=True, if_exists='replace')

            conn.execute(
                ModifyTables.set_primary_key(
                    config_src.get(dataset, 'TABLE_NAME')))

            logger.info('... done')

    logger.info('Loading and writing area codes to database')
    load_areas()
    logger.info('... done')


def modify_tables():
    """
    This function modifies tables in the database (in Docker container).

    Modification steps this function can conduct:
    - Changing the table's primary key
    - Checking whether a column exists in a given table
    - Creating a table for the alpha datasource
    - Adding geometry column
    - Adding vollcode column
    - Adding stadsdeelcode column
    - Adding hotspots column
    - Simplifying polygons in polygon column
    """
    # TODO: Refactor task: divide this function into multiple separate table modification functions.

    # simplify the polygon of the
    # buurtcombinaties: limits data traffic to the front end.
    logger.info('Enhancing tables with geographical information...')

    conn.execute(
        ModifyTables.simplify_polygon(
            'buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))

    conn.execute(
        ModifyTables.convert_to_geometry())

    for dataset in datasets:
        logger.debug('Working on %s', dataset)
        if config_src.get(dataset, 'CREATE_GEOMETRY') == 'YES':
            table_name = config_src.get(dataset, 'TABLE_NAME')
            conn.execute(ModifyTables.create_geometry_column(table_name))
            conn.execute(ModifyTables.add_vollcodes(table_name))
            conn.execute(ModifyTables.add_stadsdeelcodes(table_name))

    # do the same for alpha table
    # TODO: refactor configuration so it is not
    # needed to do this separately

    table_name = 'alpha_locations_expected'
    conn.execute(ModifyTables.create_geometry_column(table_name))
    conn.execute(ModifyTables.add_vollcodes(table_name))
    conn.execute(ModifyTables.add_stadsdeelcodes(table_name))
    conn.execute(ModifyTables.add_hotspot_names(table_name))

    logger.info('... done')


# This global dictionary is created to allow quick starting
# of ETL functions from the command line.
TASKS = {
    'areas': load_areas,
    'download': execute_download_from_objectstore,
    'parse': parse_and_write
}


def config_parser():
    """Configure commandline argument parser."""
    parser = argparse.ArgumentParser(desc)

    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1)
    parser.add_argument(
        'dataset', nargs='?', help="Upload specific dataset")

    # add options to parser
    for k, v in TASKS.items():
        parser.add_argument(
            f'--{k}', action='store_true', default=False, help=repr(v))

    return parser


def rename_quantillion_dump():

    # Get list of all data files.
    # files = os.listdir(os.getcwd() + '/data')
    files = os.listdir('/data')

    # Create regex to find Quantillion dump files.
    dumps_filter = re.compile("database\.production.*\.dump")

    # Filter all Quantillion dump files, sort them on filename
    selected_files = list(filter(dumps_filter.search, files))
    selected_files.sort()
    most_recent_dump = selected_files[-1]

    # Rename the most recent Quantillion dump to the database.
    newest_target = '/data/alpha_latest.dump'
    if os.path.isfile(newest_target):
        os.remove(newest_target)
    os.rename(f'/data/{most_recent_dump}', newest_target)
    logger.debug('renamed %s to %s', most_recent_dump, newest_target)


def main(args):
    """This is the main function of this module. Starts the ETL process."""

    # 1. make it possible to execute individual steps.
    for k, task in TASKS.items():
        if getattr(args, k):
            task()
            return

    # Parse the data and write to postgresql database.
    parse_and_write()

    # 5. Modify (pre-process) the tables in the database.
    modify_tables()


if __name__ == "__main__":
    """This function is ran when calling this module from the command line."""

    logging.basicConfig(level=logging.DEBUG)
    desc = "Importing all different data sources"

    parser = config_parser()
    args = parser.parse_args()

    LOCAL_DATA_DIRECTORY = args.targetdir[0]

    # 1. Determine which data sources are used
    p_datasets = config_src.sections()

    datasets = []

    for x in p_datasets:
        if config_src.get(x, 'ENABLE') == 'YES':
            datasets.append(x)

    # overwrite datasets, if a specific dataset is
    # given via a command line argument
    if args.dataset:
        datasets = [args.dataset]

    main(args)
