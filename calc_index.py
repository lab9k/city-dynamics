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

dbConfig = 'dev'

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

def import_data(table, colname):
	df = pd.read_sql(sql=sql.format(table), con=conn)
	if 'timestamp from' in df.columns:
		df.rename(columns={'timestamp from': 'timesetamp'}, inplace=True)
	df['timestamp'] = df['timestamp'].dt.floor('60min')
	df['day'] = [ts.weekday() for ts in df.timestamp]
	df['hour'] = [ts.hour for ts in df.timestamp]
	df.rename(columns={colname: 'drukte_index'}, inplace=True)
	return df

def min_max(x):
	x = np.array(x)
	return (x - min(x)) / (max(x) - min(x))

def calc_average_scale(df):
	df = df.groupby(['day', 'hour', 'Buurtcombinatie_code'])['drukte_index'].mean().reset_index()
	df['normalized'] = df.groupby(['day', 'Buurtcombinatie_code'])['drukte_index'].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
	return df

def merge_datasets(data):
	df = reduce(lambda x, y: pd.merge(x, y, on = ['day', 'hour', 'Buurtcombinatie_code'], how='outer'), data)
	cols = [col for col in df.columns if 'normalized' in col]
	df['normalized_index'] = df.loc[:,cols].mean(axis=1)
	return df

# create connection
conn = get_conn(dbConfig='dev')

# base call
sql = """ SELECT * FROM "{}" """

# read buurtcodes
buurtcodes = pd.read_sql(sql=sql.format('buurtcombinatie'), con=conn)

# read data sources, and round timestamp
google = import_data('google_with_bc', 'live')
gvb = import_data('gvb_with_bc', 'incoming')

# google average
google_mean = calc_average_scale(google)
gvb_mean = calc_average_scale(gvb)

# merge datasets
cols = ['day', 'hour', 'Buurtcombinatie_code', 'normalized']
df_index = merge_datasets(data=[google_mean[cols], gvb_mean[cols]])

# write to db
df_index.to_sql(name='drukteindex', con=conn, index=False, if_exists='replace')
