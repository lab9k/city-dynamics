import configparser
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import pandas as pd
import os
import logging

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_conn():
    """Create a connection to the database."""
    dbconfig = 'test'
    postgres_url = URL(
        drivername='postgresql',
        username=config_auth.get(dbconfig, 'user'),
        password=config_auth.get(dbconfig, 'password'),
        host=config_auth.get(dbconfig, 'host'),
        port=config_auth.get(dbconfig, 'port'),
        database=config_auth.get(dbconfig, 'dbname')
    )
    conn = create_engine(postgres_url)
    return conn


def main():

    testdata_dir = 'deploy/testdata/'
    datasets = os.listdir(testdata_dir)

    for dataset in datasets:
        path_to_file = os.path.join(testdata_dir, dataset)
        df = pd.read_csv(path_to_file)

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        table_name = dataset.split('.csv')[0]
        df.to_sql(table_name, con=get_conn(), if_exists='replace')


if __name__ == '__main__':
    log.info('Loading test data into database..')
    main()
    log.info('.. done.')
