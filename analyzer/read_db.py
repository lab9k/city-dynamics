import psycopg2
import configparser
import argparse
import logging
import pandas as pd

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pg_str(dbConfig):
	return 'host={} port={} user={} dbname={} password={}'.format(
		config_auth.get(dbConfig,'host'),
		config_auth.get(dbConfig,'port'), 
		config_auth.get(dbConfig,'user'), 
		config_auth.get(dbConfig,'dbname'), 
		config_auth.get(dbConfig,'password')
	)


def import_data_query(table):
	return """ SELECT * FROM "{}" """.format(table)


def main(dbConfig):
	with psycopg2.connect(get_pg_str(dbConfig)) as conn:
	# 	#with conn.cursor() as cursor:
	# 	#cursor.execute(sql)
	 	df_google = pd.read_sql(import_data_query('GOOGLE'), conn)
	return((df_gvb.shape))


if __name__ == '__main__':
	desc = 'Calculate index and write to database.'
	parser = argparse.ArgumentParser(desc)
	parser.add_argument('dbConfig', type=str, help='database config settings: dev or docker', nargs=1)
	args = parser.parse_args()
	print(main(args.dbConfig[0]))