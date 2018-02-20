import configparser
import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd
import numpy as np
import itertools

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


def set_primary_key(table):
    return """
  ALTER TABLE "{}" ADD PRIMARY KEY (index)
  """.format(table)


def concat_google(sql_query, conn):
    """Function to read google data."""

    def read_table(sql_query, conn):
        df = pd.read_sql(sql=sql_query, con=conn)
        df['timestamp'] = df.timestamp.dt.round('60min')
        df = df[['name', 'vollcode', 'timestamp', 'live', 'historical', 'stadsdeel_code', 'lat', 'lon']]
        return df

    # read raw data
    google_octnov = read_table(sql_query.format('google_with_bc'), conn=conn)
    google_dec = read_table(sql_query.format('google_dec_with_bc'), conn=conn)
    google = pd.concat([google_octnov, google_dec])
    # remove useless rows
    google = google.loc[google.historical.notnull(), :]
    del google_octnov, google_dec

    # add time data
    google['weekday'] = [ts.weekday() for ts in google.timestamp]
    google['hour'] = [ts.hour for ts in google.timestamp]

    google.to_sql(name="google_all", con=conn, if_exists='replace')

def main():
    conn = get_conn(dbconfig=args.dbConfig[0])

    sql_query = """ SELECT * FROM "{}" """

    concat_google(sql_query, conn)

    hotspots_df = pd.read_csv('lookup_tables/Amsterdam Hotspots - Sheet1.csv')

    log.debug('Writing hotspots to db..')
    hotspots_df.to_sql(name='hotspots', con=conn, if_exists='replace')
    conn.execute(set_primary_key('hotspots'))
    log.debug('..done.')

    hotspots_df = pd.read_sql("""SELECT * FROM hotspots""", conn)

    log.debug('Creating geometries on hotspots..')
    create_geom_hotspots = """
    ALTER TABLE hotspots
    ADD COLUMN point_sm geometry;

    UPDATE hotspots SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "Longitude", "Latitude"), 4326), 3857)
    """

    conn.execute(create_geom_hotspots)
    log.debug('..done.')

    log.debug('Creating geometries on Google locations..')
    create_geom_google = """
    ALTER TABLE google_all
    ADD COLUMN point_sm geometry;

    UPDATE google_all SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "lon", "lat"), 4326), 3857)
    """

    conn.execute(create_geom_google)
    log.debug('..done.')

    log.debug('Linking Google locations to hotspots..')
    join_hotspots_query = """
      DROP TABLE IF EXISTS google_all_hotspots;
      create
      table
        google_all_hotspots as with hs as(
          select
            *
          from
            "hotspots"
        ) select
          hs."Hotspot",
          hs."Latitude",
          hs."Longitude",
          google_all.*
        from
          google_all join hs on
          st_intersects(
            google_all.point_sm,
            ST_BUFFER(hs.point_sm, 100)
          )
      """

    conn.execute(join_hotspots_query)
    log.debug('..done.')

    google_hotspots = pd.read_sql(sql="SELECT * FROM google_all_hotspots", con=conn)

    # historical weekpatroon
    # first calculate the average weekpatroon per location
    google_week_location = google_hotspots.groupby([
        'hour', 'Hotspot', 'name'])['historical'].mean().reset_index()

    # and then calculate the average weekpatroon per hotspot
    google_week_hotspots = google_week_location.groupby([
        'Hotspot', 'hour'])['historical'].mean().reset_index()

    google_week_hotspots.rename(columns={'historical': 'drukteindex'}, inplace=True)

    # fill the dataframe with all missing hotspot-hour combinations
    x = {"hour": np.arange(24), "Hotspot": hotspots_df['Hotspot'].unique().tolist()}
    hs_hour_combinations = pd.DataFrame(list(itertools.product(*x.values())), columns=x.keys())
    google_week_hotspots = google_week_hotspots.merge(hs_hour_combinations, on=['hour', 'Hotspot'], how='outer')
    google_week_hotspots['drukteindex'].fillna(value=0, inplace=True)

    log.debug('Writing to db..')
    google_week_hotspots.to_sql(name='drukteindex_hotspots', con=conn, if_exists='replace')

    insert_into_models_hotspots = """
    insert into datasets_hotspotsdrukteindex (
    index,
    hour,
    drukteindex,
    hotspot_id
    ) select c.index, hour, drukteindex, h.index from hotspots h, drukteindex_hotspots c
    where  h."Hotspot" = c."Hotspot";

    insert into datasets_hotspots (
    index, 
    "Hotspot", 
    "Latitude", 
    "Longitude"
    )
    select index, "Hotspot", "Latitude", "Longitude" from hotspots;

    """

    conn.execute(insert_into_models_hotspots)

    log.debug('done.')


if __name__ == '__main__':
    desc = "Calculate index hotspots."
    log.debug(desc)
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    main()