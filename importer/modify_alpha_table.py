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

##############################################################################
def run()
    # TODO: parse input table.
    # TODO: write new table to DB.
    pass


##############################################################################
if __name__ == "__main__":
    run()