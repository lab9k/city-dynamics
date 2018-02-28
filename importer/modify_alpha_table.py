"""
This module pre-processes the Alpha table (daily dump from objectstore).

Input table: google_raw_locations_expected_acceptance
Output table: alpha_locations_expected

The dumped table originally contains multiple time intervals per line. This
should be split up into multiple single lines: one per single hour (the first
hour of the time range). In the original table, the latitude and longitude
values are combined in a tuple in a single column. These two values should be
split and given their own columns.

"""

import configparser
import argparse
import logging
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy import select

from sqlalchemy import inspect
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer, String

import json
import pandas as pd
import q

##############################################################################
config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_conn(dbconfig):
    """Create a connection to the database."""
    postgres_url = URL(
        drivername='postgresql',
        username=config_auth.get(dbconfig, 'user'),
        password=config_auth.get(dbconfig, 'password'),
        host=config_auth.get(dbconfig, 'host'),
        port=config_auth.get(dbconfig, 'port'),
        database=config_auth.get(dbconfig, 'dbname')
    )
    conn = create_engine(postgres_url)
    return conn


##############################################################################


##############################################################################
create_alpha_table = '''
DROP TABLE IF EXISTS  public.alpha_locations_expected;

CREATE TABLE  public.alpha_locations_expected(
    id              INTEGER,
    place_id        VARCHAR,
    name            TEXT,
    hour            INT4,
    expected        FLOAT8,
    lat             FLOAT8,
    lon             FLOAT8,
    address         TEXT,
    location_type   TEXT,
    visit_duration  TEXT,
    types           TEXT,
    category        INT4);
'''
##############################################################################


##############################################################################
def create_row_sql(id, place_id, name, timestamp, expected, lat, lon, address,
            location_type, visit_duration, types, category):

    row_sql = '''INSERT INTO public.alpha_locations_expected(id, \
    place_id, name, timestamp, expected, lat, lon, address, location_type, \
    visit_duration, types, category)
    VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
    ''' % (id, place_id, name, timestamp, expected, lat, lon, address,
            location_type, visit_duration, types, category)

    return row_sql

##############################################################################


##############################################################################
def run():
    log.debug("Creating modified version of Alpha dump data table..")

    # Create database connection
    conn = get_conn(dbconfig=args.dbConfig[0])

    # Load raw Alpha data dump from table
    raw = pd.read_sql_table('google_raw_locations_expected_acceptance', conn)

    # Create table for modified Alpha data
    conn.execute(create_alpha_table)
    # '''
    # Iterate over raw entries to fill new table
    id_counter = 0
    for i in range(0, len(raw)):
        id = id_counter
        place_id = raw.place_id[i]
        name = raw.name[i]

        for interval in raw.data[i]['Expected']:

            # Process timestamp (truncate to first hour)
            hour = int(interval['TimeInterval'][0:2])
            if interval['TimeInterval'][2:4] == 'pm':
                hour += 12
            if hour == 24:
                hour = 0

            expected = interval['ExpectedValue']

            q.d()
            # Create sql query to write data to database
            row_sql = create_row_sql(id, place_id, name, timestamp, expected, lat, lon, address,
                location_type, visit_duration, types, category, conn)

            # Write data to database
            conn.execute(row_sql)

            # Update id counter so all rows have a unique id.
            id_counter += 1
    # '''

    q.d()

    log.debug("..done")

##############################################################################
if __name__ == '__main__':
    desc = 'Run extra sql'
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    run()


##############################################################################
# temp = {"url": "https://www.google.com/search?q=Il Cavallino, Maasstraat 67HS, 1078 HE Amsterdam, Netherlands",
#         "name": "Il Cavallino", "types": ["restaurant", "food", "point_of_interest", "establishment"], "Category": 2,
#         "Expected": [{"TimeInterval": "5pm-6pm", "ExpectedValue": 0.19736842105263158},
#                      {"TimeInterval": "6pm-7pm", "ExpectedValue": 0.4342105263157895},
#                      {"TimeInterval": "7pm-8pm", "ExpectedValue": 0.5921052631578947},
#                      {"TimeInterval": "8pm-9pm", "ExpectedValue": 0.5526315789473685},
#                      {"TimeInterval": "9pm-10pm", "ExpectedValue": 0.3815789473684211}],
#         "location": {"type": "Point", "coordinates": [4.8955886, 52.3452768]},
#         "place_id": "ChIJFU6QdYoJxkcRiiY_jGApA3k", "BatchTime": "2018-02-24T02:16:17.131000Z", "Real-time": 0.0,
#         "ScrapeTime": "2018-02-24T02:16:21Z", "VisitDuration": "1,5 bis 3,5 uur",
#         "formatted_address": "Maasstraat 67HS, 1078 HE Amsterdam, Netherlands"}
##############################################################################