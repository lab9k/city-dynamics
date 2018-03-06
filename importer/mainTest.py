from ETLFunctions import *
import logging
import configparser
import argparse
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')


# import ETLlib

#etl = ETLlib()

#etl.tableHasPoint("google")

# ==== MAIN TEST ==== #


if __name__ == "__main__":

    # ==== MAIN ETL PIPELINE ====

    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Entering ETL pipeline..')
    parser.add_argument(
        'targetdir', type=str, help='Local data directory.', nargs=1, default='data')

    parser.add_argument('dataset', nargs='?', help="Upload specific dataset")
    args = parser.parse_args()


    # 1 --- Load data from objectstore

    # Check whether locally cached downloads should be used.
    ENV_VAR = 'EXTERNAL_DATASERVICES_USE_LOCAL'
    use_local = True if os.environ.get(ENV_VAR, '') == 'TRUE' else False

    if not use_local:
        target_dir = args.targetdir[0]
        datasets = [config_src.get(x, 'FOLDER_FTP') for x in config_src.sections()]
        conn = Connection(**OS_CONNECT)
        download_containers(conn, datasets, targetdir)

    else:
        logger.info('No download from datastore requested, quitting.')




    # Transform


if __name__ == '__main__':
    desc = 'Upload citydynamics datasets into PostgreSQL.'
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'datadir', type=str, help='Local data directory', nargs=1)

    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker', nargs=1)

    parser.add_argument('dataset', nargs='?', help="Upload specific dataset")
    args = parser.parse_args()

    p_datasets = config_src.sections()

    datasets = []

    for x in p_datasets:
        if config_src.get(x, 'ENABLE') == 'YES':
            datasets.append(x)

    if args.dataset:
        datasets = [args.dataset]

    main(args.datadir[0], args.dbConfig[0], datasets)






    tabelCreateGeoPoint("google")
    tableCreateBuurt("google")
    tableCreateGeoPoint("gvb")

    # Checks

    # some checks



    """
