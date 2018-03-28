""" MAIN ETL Pipeline

Script which executes the import pipeline:
- downloads raw data sources from objectstore, guided by the sources.conf file,
  and stores it in a local data directory.
- parses the raw data and writes it to a postgresql database
"""

import logging
import configparser
import argparse
import os

import download_from_objectstore
import parsers
from ETLFunctions import DatabaseInteractions
from ETLFunctions import ModifyTables
from ETLFunctions import LoadGebieden

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

db_int = DatabaseInteractions()
conn = db_int.get_sqlalchemy_connection()


# TODO Use this structure to refactor the main function
def download_from_os():
    os_folders = [config_src.get(x, 'OBJSTORE_FOLDER') for x in datasets]

    # Check whether locally cached downloads should be used.
    ENV_VAR = 'EXTERNAL_DATASERVICES_USE_LOCAL'
    use_local = True if os.environ.get(ENV_VAR, '') == 'TRUE' else False

    if not use_local:
        download_from_objectstore.main(LOCAL_DATA_DIRECTORY, os_folders)
    else:
        logger.info('No download from datastore requested, quitting.')


def load_gebieden():
    pg_str = db_int.get_postgresql_string()
    LoadGebieden.load_gebieden(pg_str)


def parse_and_write():
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
    load_gebieden()
    logger.info('... done')


def modify_tables():
    """
    Shitty name. what does this do.
    """

    # simplify the polygon of the
    # buurtcombinaties: limits data traffic to the front end.
    logger.info('Enhancing tables with geographical information...')

    conn.execute(
        ModifyTables.simplify_polygon(
            'buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))

    for dataset in datasets:
        if config_src.get(dataset, 'CREATE_POINT') == 'YES':
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


TASKS = {
    'gebieden': load_gebieden
}


def config_parser():
    """Configure argument parser
    """
    parser = argparse.ArgumentParser(desc)

    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1)
    parser.add_argument(
        'dataset', nargs='?', help="Upload specific dataset")

    # add options to parser
    for k in TASKS.keys():
        parser.add_argument(
            f'--{k}', action='store_true', help="Download gebieden")

    return parser


def main(args):
    # make it possible to execute individual steps
    for k, task in TASKS.items():
        if getattr(args, k):
            task()
            return

    # 2. Download data from objectstore

    download_from_os()

    # 3. Restore alpha dump to database
    cmd = 'pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --no-password --clean /data/google_raw.dump'
    os.system(cmd)

    # 4. Parse the data and write to postgresql database

    parse_and_write()

    # 5. Modify tables

    modify_tables()


if __name__ == "__main__":

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
