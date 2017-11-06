import os
import argparse
import configparser
import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# import functions for different datasets
# from importer import gvb
# from importer import mora
import gvb
# import google
import mora

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('datadir', type=str, help='Local data directory.', nargs=1)
parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
args = parser.parse_args()

# get datadir argument
datadir = args.datadir[0]
# datadir = 'data'

# get dbConfig argument
dbConfig = args.dbConfig[0]
# dbConfig = 'dev'

# parse authentication configuration
config = configparser.RawConfigParser()
config.read('auth.conf')
# config.read('importer/auth.conf')

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

# configuration for database
db_config = configparser.RawConfigParser()
db_config.read('db.conf')
# db_config.read('importer/db.conf')


# GVB to database
tablename = db_config.get('gvb', 'TABLE_NAME')
gvb.to_database(tablename=tablename, conn=conn, datadir=datadir)
print(pd.read_sql_table(table_name=tablename, con=conn).head()) # check if it worked

tablename = db_config.get('mora', 'TABLE_NAME')
mora.to_database(tablename=tablename, conn=conn, datadir=datadir)
print(pd.read_sql_table(table_name=tablename, con=conn).head(2)) # check if it worked
