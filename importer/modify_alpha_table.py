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

import logging
import pandas as pd
import re

from ETLFunctions import DatabaseInteractions
from ETLFunctions import ModifyTables

log = logging.getLogger(__name__)


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
    db_int = DatabaseInteractions()
    conn = db_int.get_sqlalchemy_connection()

    # Load raw Alpha data dump from table
    raw = pd.read_sql_table('google_raw_locations_expected_acceptance', conn)

    # Create table for modified Alpha data
    conn.execute(ModifyTables.create_alpha_table())

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

    log.debug("..done")

##############################################################################
if __name__ == '__main__':
    run()
