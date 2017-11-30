import psycopg2
import configparser
import argparse
import logging
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pg_str(dbConfig):
	return 'host={} port={} user={} dbname={} password={}'.format(
		config_auth.get(dbConfig,'host'),
		config_auth.get(dbConfig,'port'), 
		config_auth.get(dbConfig,'user'), 
		config_auth.get(dbConfig,'dbname'), 
		config_auth.get(dbConfig,'password')
	)


def import_data_query(table):
	return """ SELECT * FROM "{}" """.format(table)


def main(dbConfig):
# create connection
POSTGRES_URL = URL(
	drivername='postgresql',
	username=config_auth.get(dbConfig,'user'),
	password=config_auth.get(dbConfig,'password'),
	host=config_auth.get(dbConfig,'host'),
	port=config_auth.get(dbConfig,'port'),
	database=config_auth.get(dbConfig,'dbname')
)
conn = create_engine(POSTGRES_URL)

# read buurtcodes
buurtcodes = pd.read_sql(import_data_query('buurtcombinatie'), conn)

# read google, and round timestamp
df_google = pd.read_sql(import_data_query('google_with_bc'), conn)
df_google['timestamp_hour'] = df_google['timestamp'].dt.floor('60min')

# google average
df_index = df_google.groupby(['timestamp_hour', 'Buurtcombinatie_code'])['live'].mean().reset_index()

# change column name
df_index.rename(columns={'live': 'drukte_index'}, inplace=True)

# add buurtcodes
df_index = pd.merge(df_index, buurtcodes, on='Buurtcombinatie_code')

# select columns

# df_index = df_index[cols]

# write to db
df_index.to_sql(name='drukteindex', con=conn, index=False, if_exists='replace')


if __name__ == '__main__':
	desc = 'Calculate index and write to database.'
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	print(main(args.dbConfig[0]))