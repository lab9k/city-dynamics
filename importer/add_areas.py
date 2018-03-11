"""
This is where SQL queries that must be run after import go.
"""

import configparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# parse authentication configuration
config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

tables_to_modify = [config_src.get(x, 'TABLE_NAME') for x in config_src.sections() if
                    config_src.get(x, 'CREATE_POINT') == 'YES']


def main(dbConfig, datasets):
    execute_sql(pg_str, simplify_polygon('buurtcombinatie'))

    for dataset in datasets:
        table_name = config_src.get(dataset, 'TABLE_NAME')
        logger.info('Handling {} table'.format(table_name))
        execute_sql(pg_str, create_geometry_query(table_name))
        execute_sql(pg_str, add_bc_codes(table_name))
        execute_sql(pg_str, set_primary_key(table_name + '_with_bc'))
