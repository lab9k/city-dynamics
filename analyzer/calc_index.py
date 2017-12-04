import configparser
import argparse
import logging
import pandas as pd

from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_conn(dbConfig):
	POSTGRES_URL = URL(
		drivername='postgresql',
		username=config_auth.get(dbConfig,'user'),
		password=config_auth.get(dbConfig,'password'),
		host=config_auth.get(dbConfig,'host'),
		port=config_auth.get(dbConfig,'port'),
		database=config_auth.get(dbConfig,'dbname')
	)
	conn = create_engine(POSTGRES_URL)
	return conn

def min_max(x):
	x = np.array(x)
	return (x - min(x)) / (max(x) - min(x))

def normalize(df):
	df = df.groupby(['vollcode', 'timestamp'])['drukte_index'].mean().reset_index()
	df['normalized'] = df.groupby(['timestamp'])['drukte_index'].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
	df.groupby('vollcode')['normalized'].max()
	return df

def import_data(table, colname, sql_query, conn):
	df = pd.read_sql(sql=sql_query.format(table), con=conn)
	if 'timestamp from' in df.columns:
		df.rename(columns={'timestamp from': 'timesetamp'}, inplace=True)
	df['timestamp'] = df['timestamp'].dt.floor('60min')
	df['day'] = [ts.weekday() for ts in df.timestamp]
	df['hour'] = [ts.hour for ts in df.timestamp]
	df.rename(columns={colname: 'drukte_index'}, inplace=True)
	df = normalize(df)
	return df

def merge_datasets(data):
	df = reduce(lambda x, y: pd.merge(x, y, on = ['timestamp', 'vollcode'], how='outer'), data)
	cols = [col for col in df.columns if 'normalized' in col]
	df['normalized_index'] = df.loc[:,cols].mean(axis=1)
	return df

def main():
# create connection
conn = get_conn(dbConfig=args.dbConfig[0])

# base call
sql_query = """ SELECT * FROM "{}" """

# read buurtcodes
buurtcodes = pd.read_sql(sql=sql_query.format('buurtcombinatie'), con=conn)

# verblijversindex
verblijversindex = pd.read_sql(sql=sql_query.format('VERBLIJVERSINDEX'), con=conn)

# read data sources, and round timestamp
google = import_data('google_with_bc', 'live', sql_query, conn)
gvb = import_data('gvb_with_bc', 'incoming', sql_query, conn)

# merge datasets
cols = ['vollcode', 'normalized']
df_index = merge_datasets(data=[google[cols], gvb[cols]])

# write to db
df_index.to_sql(name='drukteindex', con=conn, index=False, if_exists='replace')

if __name__ == '__main__':
	desc = "Calculate index."
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	main()