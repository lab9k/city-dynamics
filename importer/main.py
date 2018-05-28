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
from parsers.parse_helper_functions import DatabaseInteractions
#import parsers.parse_alpha
from parsers import parse_alpha
from parsers import parse_gvb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

db_int = DatabaseInteractions()
conn = db_int.get_sqlalchemy_connection()

def rename_quantillion_dump():

    # Get list of all data files.
    # LOCAL:
    files = os.listdir(os.getcwd() + '/data')
    # DOCKER:
    #files = os.listdir('/data')

    # Create regex to find Quantillion dump files.
    dumps_filter = re.compile("database\.production.*\.dump")

    # Filter all Quantillion dump files, sort them on filename
    selected_files = list(filter(dumps_filter.search, files))
    selected_files.sort()
    most_recent_dump = selected_files[-1]

    # Rename the most recent Quantillion dump to the database.
    newest_target = 'data/alpha_latest.dump'
    if os.path.isfile(newest_target):
        os.remove(newest_target)
    os.rename(f'data/{most_recent_dump}', newest_target)
    logger.debug('renamed %s to %s', most_recent_dump, newest_target)


def execute_download_from_objectstore(objectstore_containers):
    """This function downloads data for all ENABLED containers in importer/sources.conf from the objectstore."""

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


def main(args):
    """This is the main function of this module. Starts the ETL process."""

    objectstore_containers = ['quantillion_dump',
                              'GVB',
                              'hotspots',
                              #'geo_mapping',
                              'parkeer_occupancy/2018_w08_w17_occupancy_v2',
                              #'afval',
                              #'CMSA',
                              #'tellus',
                              'verblijversindex',
                              #'MORA',
                              ]

    execute_download_from_objectstore(objectstore_containers)

    #parse_alpha()
    parse_gvb.load_parsed_file(LOCAL_DATA_DIRECTORY)

    # parsers.parse_hotspots()

    # parsers.parse_buurtcombinatie()
    # parse_stadsdeel_buurtcombinatie()
    # parsers.parse_parkeren()
    # parsers.parse_afval()
    # parsers.parse_cmsa()
    # parsers.parse_tellus()
    # parsers.parse_verblijversindex
    # parsers.parse_mora()
    # parsers.parse_functiekaart()
    # parsers.parse_geomapping()


if __name__ == "__main__":
    """This function is ran when calling this module from the command line."""

    # Enable logging
    logging.basicConfig(level=logging.DEBUG)
    desc = "Importing all different data sources"

    # Parse command line arguments to get targetdir.
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1)
    args = parser.parse_args()
    LOCAL_DATA_DIRECTORY = args.targetdir[0]

    # Run main parsing script.
    main(LOCAL_DATA_DIRECTORY)
