import csv
import sys
import os
import argparse
import django
import configparser

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


# parse arguments (now only datadir)
# parser = argparse.ArgumentParser()
# parser.add_argument('datadir', type=str, help='Local data directory.', nargs=1)
# args = parser.parse_args()

# add project dir to path
# may only be necessary for local dev?
project_dir = '/home/rluijk/Documents/gitrepos/city-dynamics/web/'
sys.path.append(project_dir)

# add settings.py to environmental variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'citydynamics.settings'

# setup Django using settings
django.setup()

# read data
df = pd.read_csv('/home/rluijk/Documents/gitrepos/city-dynamics/data/dummy_data.csv')



config = configparser.RawConfigParser()
# config.read('auth.conf')
config.read('/home/rluijk/Documents/gitrepos/city-dynamics/importer/auth.conf')

dbConfig = 'dev'
LOCAL_POSTGRES_URL = URL(
    drivername='postgresql',
    username=config.get(dbConfig,'user'),
    password=config.get(dbConfig,'password'),
    host=config.get(dbConfig,'host'),
    port=config.get(dbConfig,'port'),
    database=config.get(dbConfig,'dbname')
)


# to database
name = 'mytable'
conn = create_engine(LOCAL_POSTGRES_URL)
df.to_sql(name=name, con=conn, index=False, if_exists='append')

# alternative method
# conn = psycopg2.connect("dbname=city-dynamics user=city-dynamics password=insecure host=localhost port=5403")

# check that it worked
pd.read_sql('SELECT * FROM mytable', conn)
