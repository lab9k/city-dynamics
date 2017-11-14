import os
import argparse
import configparser
import datetime
import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import parsers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf') 

datasets = config_src.sections()


def main(datadir, dbConfig):
	config_auth = configparser.RawConfigParser()
	config_auth.read('auth.conf') 

	LOCAL_POSTGRES_URL = URL(
		drivername='postgresql',
		username=config_auth.get(dbConfig,'user'),
		password=config_auth.get(dbConfig,'password'),
		host=config_auth.get(dbConfig,'host'),
		port=config_auth.get(dbConfig,'port'),
		database=config_auth.get(dbConfig,'dbname')
	)

	conn = create_engine(LOCAL_POSTGRES_URL)
	logger.info('Created database connection')

	for dataset in datasets:
		logger.info('Parsing and writing {} data...'.format(dataset))
		getattr(parsers, 'parse_' + dataset)(tablename=config_src.get(dataset, 'TABLE_NAME'), conn=conn, datadir=datadir)
		logger.info('... done')


if __name__ == '__main__':
	desc = 'Upload city-dynamics datasets into PostgreSQL.'
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('datadir', type=str, help='Local data directory', nargs=1)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	main(args.datadir[0], args.dbConfig[0])