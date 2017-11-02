def read_write_testje(files, *args):
    file = [file for file in files if args[0] in file]
    if len(file) > 1:
        print('Multiple files match!')
        return None
    elif len(file) == 0:
        print('No files match!')
        return None
    df = pd.read_csv(file[0])
    df.to_sql(name=args[1], con=conn, index=False, if_exists='append')


import os
import argparse
import configparser

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('datadir', type=str, help='Local data directory.', nargs=1)
parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
args = parser.parse_args()

# get datadir argument
datadir = args.datadir[0]

# get dbConfig argument
dbConfig = args.dbConfig[0]

# list all files in data folder
filelist = [os.path.join(datadir, file) for file in os.listdir(datadir)]

# parse authentication configuration
config = configparser.RawConfigParser()
config.read('auth.conf')

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
name = 'mytable'
conn = create_engine(LOCAL_POSTGRES_URL)

# read testje and write to db
read_write_testje(filelist, 'dummy', 'mytable')

# check if it worked
print(pd.read_sql('SELECT * FROM mytable', conn))