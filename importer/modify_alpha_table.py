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
import pandas as pd
import re

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
    url             TEXT,
    weekday         INT4,
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
def create_row_sql(id, place_id, name, url, weekday, hour, expected, lat, lon,
                   address, location_type, visit_duration, types, category):
    row_sql = '''INSERT INTO public.alpha_locations_expected(id, \
    place_id, name, url, weekday, hour, expected, lat, lon, address, \
    location_type, visit_duration, types, category)
    VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
    ''' % (id, place_id, name, url, weekday, hour, expected, lat, lon, address,
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

    # Lambda function to double up quotation marks for sql writing.
    fix_quotes = lambda x: re.sub("'", "''", x)

    # Iterate over raw entries to fill new table
    id_counter = 0
    for i in range(0, len(raw)):
        place_id = raw.place_id[i]
        name = raw.name[i]
        url = raw.data[i]['url']
        weekday = raw.scraped_at[i].weekday()
        lat = raw.data[i]['location']['coordinates'][1]
        lon = raw.data[i]['location']['coordinates'][0]
        address = raw.data[i]['formatted_address']
        location_type = raw.data[i]['location']['type']
        visit_duration = raw.data[i]['VisitDuration']
        types = str(raw.data[i]['types'])
        category = raw.data[i]['Category']

        # Fix quotes for sql writing
        name = fix_quotes(name)
        url = fix_quotes(url)
        address = fix_quotes(address)
        location_type = fix_quotes(location_type)
        visit_duration = fix_quotes(visit_duration)
        types = fix_quotes(types)

        # Loop over all expected hour intervals for each location and scrape day
        for interval in raw.data[i]['Expected']:

            # Truncate time interval to first hour of the interval
            hour = interval['TimeInterval'][0:2]
            hour = int(re.sub("[^0-9]", "", hour))
            ampm = interval['TimeInterval'][1:4]
            ampm = re.sub('[^a-zA-Z]+', '', ampm)
            if ampm == 'pm':
                if hour == 12:
                    pass
                else:
                    hour += 12

            # Get the expected crowdedness value for this hour (relative value)
            expected = interval['ExpectedValue']

            # Create sql query to write data to database
            row_sql = create_row_sql(id_counter, place_id, name, url, weekday, hour, expected,
                                     lat, lon, address, location_type, visit_duration, types, category)

            # Write data to database
            conn.execute(row_sql)

            # Update id counter so all rows have a unique id
            id_counter += 1

    # add vollcode and stadsdeel_code

    add_vollcode_stadsdeel_code = """
    
    ALTER TABLE alpha_locations_expected
    DROP COLUMN IF EXISTS geom;
    ALTER TABLE alpha_locations_expected
    ADD COLUMN geom geometry;
    UPDATE alpha_locations_expected
    SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);

    alter table alpha_locations_expected
    add column vollcode varchar;
    UPDATE alpha_locations_expected
    SET vollcode = buurtcombinatie.vollcode
    FROM buurtcombinatie
    WHERE st_intersects(alpha_locations_expected.geom, buurtcombinatie.wkb_geometry);

    alter table alpha_locations_expected
    add column stadsdeel_code varchar;
    UPDATE alpha_locations_expected
    SET stadsdeel_code = stadsdeel.code
    FROM stadsdeel
    WHERE st_intersects(alpha_locations_expected.geom, stadsdeel.wkb_geometry);
    """

    conn.execute(add_vollcode_stadsdeel_code)

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
