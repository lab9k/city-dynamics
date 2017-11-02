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

def fix_times(t, d):
	if t >= 24:
		t -= 24
		if d == 1:
			d = 7
		else:
			d -= 1	
	return t, d

def get_datetime(row):
    t = datetime.time(row.tijd_numeric, 0)
    d = [int(e) for e in row.date.split('-')]    
    d = datetime.date(d[0], d[1], d[2])
    dt = datetime.datetime.combine(d, t)
    return dt

def read_write_gvb(rittenpath='GVB/Ritten GVB 24jun2017-7okt2017.csv', locationspath='GVB/Ortnr - coordinaten (ingangsdatum dec 2015) met LAT LONG.xlsx', name='GVB'):
    
    # read raw ritten
    rittenpath = os.path.join(datadir, rittenpath)
    ritten = pd.read_csv(rittenpath, skiprows=2, header=None)
    ritten.columns = ['weekdag', 'tijdstip', 'ortnr_start', 'haltenaam_start', 'ortnr_eind', 'tot_ritten']
    ritten.drop('haltenaam_start', axis=1, inplace=True)
    
    # read locations
    locationspath = os.path.join(datadir, locationspath)
    locations = pd.read_excel(locationspath)
    locations.drop(['X_COORDINAAT', 'Y_COORDINAAT'], axis=1, inplace=True)
    
    # drop unknown haltes
    locations = locations.loc[locations.haltenaam != '-- Leeg beeld --']
    
    # add start to ritten
    newnames = dict(OrtNr='ortnr_start', haltenaam='haltenaam_start', LAT='lat_start', LONG='lng_start')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_start')
    
    # add end to ritten
    newnames = dict(ortnr_start='ortnr_eind', haltenaam_start='haltenaam_eind', lat_start='lat_eind', lng_start='lng_eind')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_eind')
    
    # incoming ritten
    incoming = ritten.groupby(['haltenaam_eind', 'weekdag', 'tijdstip'])['tot_ritten'].sum().reset_index()
    incoming.rename(columns={'haltenaam_eind':'halte', 'tot_ritten':'incoming'}, inplace=True)
    
    # outgoing ritten
    outgoing = ritten.groupby(['haltenaam_start', 'weekdag', 'tijdstip'])['tot_ritten'].sum().reset_index()
    outgoing.rename(columns={'haltenaam_start': 'halte', 'tot_ritten':'outgoing'}, inplace=True)
    
    # merge incoming, outgoing
    inout = pd.merge(incoming, outgoing, on=['halte', 'weekdag', 'tijdstip'])
    
    # del incoming, outgoing, data
    del incoming, outgoing, ritten
    
    # fix tijdstip to hour
    inout['tijd'] = [t.split(':')[0] + ':00' for t in inout.tijdstip]
    
    # aggregate to hour
    inout = inout.groupby(['halte', 'weekdag', 'tijd'])['incoming', 'outgoing'].sum().reset_index()
    
    # dag van de week to numeric
    days = dict(ma=1, di=2, wo=3, do=4, vr=5, za=6, zo=7)
    inout['day_numeric'] = [days[d] for d in inout.weekdag]
        
    # time range
    inout['tijd_numeric'] = [int(t.split(':')[0]) for t in inout.tijd]

    # fix hour over 24
    inout.drop('weekdag', axis=1, inplace=True)
    fixed_time_day = [fix_times(t, d) for t, d in zip(inout.tijd_numeric, inout.day_numeric)]
    inout['tijd_numeric'] = [x[0] for x in fixed_time_day]
    inout['day_numeric'] = [x[1] for x in fixed_time_day]

    # add timestamp, fake date, mon 2 oct - sun 8 oct
    dates = ['2017-10-0' + str(i) for i in range(2, 9)]
    inout['date'] = [dates[d-1] for d in inout.day_numeric]
    inout['timestamp'] = [get_datetime(row) for _, row in inout.iterrows()]    
    
    # mean locaties
    locations.rename(columns={'ortnr_eind':'ortnr', 'haltenaam_eind':'halte', 'lat_eind':'lat', 'lng_eind':'lng'}, inplace=True)
    mean_locations = locations.groupby('halte')['lat', 'lng'].mean().reset_index()
    mean_locations = mean_locations[mean_locations.halte != '-- Leeg beeld --']
    
    # add lat/long coordinates
    inout = pd.merge(inout, mean_locations, on='halte')
    
    # drop obsolete columns
    inout.drop(['tijd_numeric', 'tijd', 'date'], axis=1, inplace=True)
    
    # write to database
    inout.to_sql(name=name, con=conn, index=False, if_exists='append')


import os
import argparse
import configparser
import datetime

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
conn = create_engine(LOCAL_POSTGRES_URL)

# read testje and write to db
read_write_testje(filelist, 'dummy', 'mytable')

# read testje and write to db
read_write_gvb()