import configparser
import argparse
import logging
import json
import requests
import time
import pandas as pd
import numpy as np

from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from datetime import date, datetime, timedelta

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

def datetime_range(start, end, delta):
	current = start
	if not isinstance(delta, timedelta):
		delta = timedelta(**delta)
	while current < end:
		yield current
		current += delta

def min_max(x):
	x = np.array(x)
	return (x - min(x)) / (max(x) - min(x))

def normalize(x):
	return (x - x.min()) / (x.max() - x.min())

def normalize_df(df):
	# average per area code, timestamp (rounded to the hour)
	df = df.groupby(['vollcode', 'timestamp'])['drukte_index'].mean().reset_index()
	# scale per timestamp (rounded to the hour)
	df['normalized'] = df.groupby(['timestamp'])['drukte_index'].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
	return df

def import_verblijversindex(sql_query, conn):
	verblijversindex = pd.read_sql(sql=sql_query.format('VERBLIJVERSINDEX'), con=conn)
	verblijversindex = verblijversindex[['wijk', 'oppervlakte_m2']]
	verblijversindex.rename(columns={'wijk': 'vollcode'}, inplace=True)
	verblijversindex['normalized_m2'] = normalize(verblijversindex.oppervlakte_m2)
	return verblijversindex

def import_data(table, colname, sql_query, conn):
	df = pd.read_sql(sql=sql_query.format(table), con=conn)
	if 'timestamp from' in df.columns:
		df.rename(columns={'timestamp from': 'timestamp'}, inplace=True)
	df['timestamp'] = df['timestamp'].dt.floor('60min')
	df['day'] = [ts.weekday() for ts in df.timestamp]
	df['hour'] = [ts.hour for ts in df.timestamp]
	df.rename(columns={colname: 'drukte_index'}, inplace=True)
	df['drukte_index'] = df['drukte_index'].astype(float)
	df = normalize_df(df)
	return df

def import_tellus(table, colname, sql_query, conn, vollcodes):
	df = pd.read_sql(sql=sql_query.format(table), con=conn)
	df = df[['meetwaarde', 'timestamp', 'vollcode']]
	df.rename(columns={'meetwaarde':'drukte_index'}, inplace=True)
	df['drukte_index'] = df['drukte_index'].astype(int)
	df = df.groupby('timestamp')['drukte_index'].sum().reset_index()
	df['date'] = [ts.date() for ts in df.timestamp]

	data = []
	for vc in vollcodes:
		new_df = df.copy()
		new_df['vollcode'] = vc
		data.append(new_df)

	df = pd.concat(data, ignore_index=True)

	df['normalized'] = df.groupby(['date'])['drukte_index'].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
	df = df[['timestamp', 'drukte_index', 'normalized', 'vollcode']]
	return df

def merge_datasets(data):
	return reduce(lambda x, y: pd.merge(x, y, on = ['timestamp', 'vollcode'], how='outer'), data)

def complete_ts_vollcode(data, vollcodes):
	# get list of timestamps
	start = np.min(data.timestamp)
	end = np.max(data.timestamp)
	timestamps = pd.date_range(start=start, end=end, freq='H')
	# timestamps = [dt for dt in datetime_range(start, end, {'days': 0, 'hours': 1})]

	# add multi-index
	mind = pd.MultiIndex.from_product([timestamps, vollcodes])
	data = data.reindex(mind, fill_value=np.nan).reset_index()

	# drop columns
	data.drop(['vollcode', 'timestamp'], axis=1, inplace=True)

	# rename columns
	data.rename(columns={'level_0':'timestamp', 'level_1':'vollcode'}, inplace=True)

	return data


def main():
	# create connection
	conn = get_conn(dbConfig=args.dbConfig[0])

	# base call
	sql_query = """ SELECT * FROM "{}" """

	# read buurtcodes
	buurtcodes = pd.read_sql(sql=sql_query.format('buurtcombinatie'), con=conn)

	# verblijversindex
	verblijversindex = import_verblijversindex(sql_query=sql_query, conn=conn)

	# read data sources, and round timestamp
	google = import_data('google_with_bc', 'live', sql_query, conn)
	gvb = import_data('gvb_with_bc', 'incoming', sql_query, conn)
	vollcodes_centrum = [bc for bc in buurtcodes.vollcode.unique() if 'A' in bc]
	tellus = import_tellus('tellus_with_bc', 'meetwaarde', sql_query, conn, vollcodes=vollcodes_centrum)

	# merge datasets
	cols = ['vollcode', 'timestamp', 'normalized']
	data = [google[cols], gvb[cols], tellus[cols]]
	df = merge_datasets(data=data)

	# fill in missing timestamp-vollcode combinations
	all_vollcodes = [bc for bc in buurtcodes.vollcode.unique()]
	df = complete_ts_vollcode(data=df, vollcodes=all_vollcodes)

	# add buurtcode information
	df = pd.merge(df, buurtcodes, on='vollcode', how='left')

	# add verblijversindex
	df = pd.merge(df, verblijversindex, on='vollcode', how='left')

	# calculate overall index
	cols = [col for col in df.columns if 'normalized' in col]
	df['drukte_index'] = df[cols].mean(axis=1)

	# drop obsolete columns
	df.drop(cols, axis=1, inplace=True)

	# write to db
	df.to_sql(name='drukteindex', con=conn, index=True, if_exists='replace')
	conn.execute('ALTER TABLE "drukteindex" ADD PRIMARY KEY ("index")')


if __name__ == '__main__':
	desc = "Calculate index."
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	main()