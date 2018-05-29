import configparser
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import pandas as pd
import logging

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_conn():
    """Create a connection to the database."""
    dbconfig = 'docker'
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
    conn = get_conn()

    target_dir = 'deploy/testdata/'

    df = pd.read_sql(sql='SELECT * FROM "verblijversindex"', con=conn)
    df.to_csv(target_dir + 'verblijversindex.csv')

    df = pd.read_sql(sql="SELECT * FROM alpha_locations_expected WHERE hotspot = 'Central Station'", con=conn)
    df.to_csv(target_dir + 'alpha_locations_expected.csv')

    df = pd.read_sql(sql="SELECT * FROM gvb WHERE vollcode = 'A01'", con=conn)
    df.to_csv(target_dir + 'gvb.csv', index=False)


if __name__ == '__main__':
    log.info('Creating test data..')
    main()
    log.info('.. done.')