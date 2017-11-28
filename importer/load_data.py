import os
import argparse
import configparser
import datetime
import logging
import subprocess

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import parsers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_src = configparser.RawConfigParser()
config_src.read('sources.conf') 

datasets = config_src.sections()

class NonZeroReturnCode(Exception):
    pass

def scrub(l):
    out = []
    for x in l:
        if x.strip().startswith('PG:'):
            out.append('PG: <CONNECTION STRING REDACTED>')
        else:
            out.append(x)
    return out

def run_command_sync(cmd, allow_fail=False):
    logging.debug('Running %s', scrub(cmd))
#    logging.debug('Running %s', cmd)
    p = subprocess.Popen(cmd)
    p.wait()

    if p.returncode != 0 and not allow_fail:
        raise NonZeroReturnCode

    return p.returncode

def wfs2psql(url, pg_str, layer_name, **kwargs):
    cmd = ['ogr2ogr','-overwrite','-t_srs', 'EPSG:4326', '-nln', layer_name, '-F', 'PostgreSQL', pg_str, url]
    run_command_sync(cmd)

def get_pg_str(host, port, user, dbname, password):
    return 'PG:host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )

def load_gebieden(pg_str):
    areaNames = ['stadsdeel', 'buurt', 'buurtcombinatie', 'gebiedsgerichtwerken']
    srsName = 'EPSG:4326'
    for areaName in areaNames:
        WFS="https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&SERVICE=wfs&Version=2.0.0&SRSNAME=" + srsName + "&typename=" + areaName
        wfs2psql(WFS, pg_str , areaName)
        print(areaName + ' loaded into PG.')


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
	pg_str = get_pg_str(config_auth.get(dbConfig,'host'),config_auth.get(dbConfig,'port'),config_auth.get(dbConfig,'dbname'), config_auth.get(dbConfig,'user'), config_auth.get(dbConfig,'password'))
	print(pg_str)

	logger.info('Created database connection')

	for dataset in datasets:
		logger.info('Parsing and writing {} data...'.format(dataset))
		df = getattr(parsers, 'parse_' + dataset)(datadir=datadir)
		df.to_sql(name=config_src.get(dataset, 'TABLE_NAME'), con=conn, index=True, if_exists='replace')
		conn.execute('ALTER TABLE "{}" ADD PRIMARY KEY ("index");'.format(config_src.get(dataset, 'TABLE_NAME')))
		logger.info('... done')
	logger.info('Loading and writing area codes to database')
	load_gebieden(pg_str)


if __name__ == '__main__':
	desc = 'Upload city-dynamics datasets into PostgreSQL.'
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('datadir', type=str, help='Local data directory', nargs=1)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	main(args.datadir[0], args.dbConfig[0])