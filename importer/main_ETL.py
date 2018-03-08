""" MAIN ETL Pipeline

Script which executes the import pipeline:
- downloads raw data sources from objectstore, guided by the sources.conf file, and stores it in a local data directory.
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
import modify_alpha_table

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
        download_from_objectstore.main(local_data_directory, os_folders)
    else:
        logger.info('No download from datastore requested, quitting.')

def parse_and_write():

    for dataset in datasets:
        logger.info('Parsing and writing {} data...'.format(dataset))
        df = getattr(parsers, 'parse_' + dataset)(datadir=local_data_directory)
        df.to_sql(
            name=config_src.get(dataset, 'TABLE_NAME'),
            con=conn, index=True, if_exists='replace')

        conn.execute(ModifyTables.set_primary_key(config_src.get(dataset, 'TABLE_NAME')))

        logger.info('... done')

    logger.info('Loading and writing area codes to database')

    pg_str = db_int.get_postgresql_string()
    LoadGebieden.load_gebieden(pg_str)
    logger.info('... done')

def modify_tables():
    # simplify the polygon of the buurtcombinaties: limits data traffic to the front end.
    conn.execute(ModifyTables.simplify_polygon('buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))

    for dataset in datasets:
        if config_src.get(dataset, 'CREATE_POINT') == 'YES':
            conn.execute(ModifyTables.simplify_polygon('buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))
            execute_sql(pg_str, create_geometry_query(table_name))
            execute_sql(pg_str, add_bc_codes(table_name))


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    desc = "Download data from object store."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1)
    parser.add_argument('dataset', nargs='?', help="Upload specific dataset")
    args = parser.parse_args()
    local_data_directory = args.targetdir[0]

    # ==== MAIN ETL PIPELINE ====

    # 1. Determine which data sources are used

    p_datasets = config_src.sections()

    datasets = []

    for x in p_datasets:
        if config_src.get(x, 'ENABLE') == 'YES':
            datasets.append(x)

    # overwrite datasets, if a specific dataset is given via a command line argument
    if args.dataset:
        datasets = [args.dataset]

    ###

    # 2. Download data from objectstore

    download_from_os()

    # 3. Parse the data and write to postgresql database

    parse_and_write()

    # 4. Modify alpha table
    modify_alpha_table.run()

    # 5. Modify tables

    modify_tables()
