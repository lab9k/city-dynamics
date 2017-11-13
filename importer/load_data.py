import os
import argparse
import configparser
import datetime
import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# import functions for different datasets
# from importer import gvb # local dev
# from importer import mora # local dev
import gvb # in docker
import mora # in docker
import google

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('datadir', type=str, help='Local data directory.', nargs=1)
parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
args = parser.parse_args()

# get datadir argument
datadir = args.datadir[0] # in docker
# datadir = 'data' # local dev

# get dbConfig argument
dbConfig = args.dbConfig[0] # in docker
# dbConfig = 'dev' # local dev

# parse authentication configuration
config = configparser.RawConfigParser()
config.read('auth.conf') # in docker
# config.read('importer/auth.conf') # local dev

# create postgres URL
LOCAL_POSTGRES_URL = URL(
    drivername='postgresql',
    username=config.get(dbConfig,'user'),
    password=config.get(dbConfig,'password'),
    host=config.get(dbConfig,'host'),
    port=config.get(dbConfig,'port'),
    database=config.get(dbConfig,'dbname')
)

# connect to database
conn = create_engine(LOCAL_POSTGRES_URL)
logger.info('Created database connection')

# configuration for database
db_config = configparser.RawConfigParser()
db_config.read('db.conf') # in docker
# db_config.read('importer/db.conf') # local dev

# GVB to database
tablename = db_config.get('gvb', 'TABLE_NAME')
logger.info('Parsing and writing GVB data...')
gvb.to_database(tablename=tablename, conn=conn, datadir=datadir)
logger.info('... done')
# print(pd.read_sql_table(table_name=tablename, con=conn).head()) # check if it worked

# MORA to database
tablename = db_config.get('mora', 'TABLE_NAME')
logger.info('Parsing and writing MORA data...')
mora.to_database(tablename=tablename, conn=conn, datadir=datadir)
logger.info('... done')

# print(pd.read_sql_table(table_name=tablename, con=conn).head(2)) # check if it worked

# Google to database
tablename = db_config.get('google', 'TABLE_NAME')
logger.info('Parsing and writing Google data...')
google.to_database(tablename=tablename, conn=conn, datadir=datadir)
logger.info('... done')
# print(pd.read_sql_table(table_name=tablename, con=conn).head(2)) # check if it worked
