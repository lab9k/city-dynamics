"""
MAIN ETL Pipeline

Module executes the import pipeline:
    - Download raw data sources from objectstore, guided by the sources.conf file.
    - Store this data in a local data directory.
    - Parse the raw data and write the results to postgresql database (in Docker container).
"""

# Imports generic Python libraries.
import logging
import argparse
import configparser
import os
import os.path
import re

# Import own modules.
import download_from_objectstore
from parsers.parse_helper_functions import DatabaseInteractions
# from parsers import *
from parsers import parse_alpha
from parsers import parse_gvb
from parsers import parse_hotspots
from parsers import parse_verblijversindex
from parsers import parse_parkeren
from parsers import parse_gebieden

# Enable logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse the sources.conf file. Result: a 'CONFIG' dict of all enabled sources.
CONFIG_SRC = configparser.ConfigParser()
CONFIG_SRC.optionxform = str
CONFIG_SRC.read('sources.conf')
CONFIG_ALL = {s: dict(CONFIG_SRC.items(s)) for s in CONFIG_SRC.sections()}
CONFIG = {k: v for k, v in CONFIG_ALL.items() if v['ENABLE']=='YES'}


# Create database connection.
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
    """
    This function downloads data for all ENABLED containers
    in importer/sources.conf from the objectstore.
    """

    # Check whether locally cached downloads should be used.
    ENV_VAR = 'EXTERNAL_DATASERVICES_USE_LOCAL'
    use_local = True if os.environ.get(ENV_VAR, '') == 'TRUE' else False

    if not use_local:
        if not DATA_ROOT:
            raise ValueError("data dir missing")
        download_from_objectstore.main(objectstore_containers, DATA_ROOT)
    else:
        logger.info('No download from datastore requested, quitting.')

    # rename quantillion dump if it's there
    try:
        rename_quantillion_dump()
    except:
        pass


def parse_datasets():
    """
    This function parses the data downloaded from the objectstore
    and writes it to the database (Docker container).
    """

    for dataset, config in CONFIG.items():
        logger.info(f'Parsing the \"{dataset}\" dataset...\n')

        # Get parser for dataset based on the dataset identifier/name.
        # parser = eval("parsers.parse_" + dataset)
        # df = parser.run(conn=conn, data_root=DATA_ROOT, **config)

        run_parser = getattr(eval("parse_" + dataset), "run")
        df = run_parser(conn=conn, data_root=DATA_ROOT, **config)

        # If parser does not return a dataframe, continue to next dataset.
        if df is None:
            continue

        logger.info('... done')



def main():
    """This is the main function of this module. Starts the ETL process."""

    # Get objectstore container names from config file and download their data.
    objectstore_containers = [v['OBJSTORE_CONTAINER'] for v in CONFIG.values()]
    # execute_download_from_objectstore(objectstore_containers)

    # Parse all source data and write results to database (@ Docker container).
    parse_datasets()

    # Order is important; 'gebieden' and 'hotspots' need to run first,
    # since they contain geo-information for other sources.
    # parse_parkeren.main(LOCAL_DATA_DIRECTORY, conn=conn)


def parse_commandine_args():
    """Configure commandline argument parser."""
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1)
    parser.add_argument(
        'dataset', nargs='?', help="Upload specific dataset")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    """This function is ran when calling this module from the command line."""

    # Log data import process.
    logging.basicConfig(level=logging.DEBUG)
    desc = "Importing all different data sources"

    # Parse commandline arguments.
    args = parse_commandine_args()
    DATA_ROOT = args.targetdir[0]

    # Overwrite datasets when a specific dataset is given as command line arg.
    if args.dataset:
        CONFIG = {args.dataset: CONFIG[args.dataset]}

    # Call the main import routine.
    main()
