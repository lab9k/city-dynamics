import psycopg2
import configparser
import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd

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


def execute_sql(pg_str, sql):
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def get_pg_str(host, port, user, dbname, password):
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


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

    #TO BE DELETED / REFACTORED
    pg_str = get_pg_str('localhost', '5432', 'citydynamics', 'citydynamics', 'insecure')


    sql_query = """ SELECT * FROM "{}" """

    concat_google(sql_query, conn)
    hotspots_df = pd.read_csv('lookup_tables/Amsterdam Hotspots - Sheet1.csv')

    hotspots_df.to_sql(name='hotspots', con=conn, if_exists='replace')
    execute_sql(pg_str, set_primary_key('hotspots'))

    create_geom_hotspots = """
    ALTER TABLE hotspots
    ADD COLUMN point_sm geometry;

    UPDATE hotspots SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "Longitude", "Latitude"), 4326), 3857)
    """

    execute_sql(pg_str, create_geom_hotspots)

    create_geom_google = """
    ALTER TABLE google_all
    ADD COLUMN point_sm geometry;

    UPDATE google_all SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "lon", "lat"), 4326), 3857)
    """

    execute_sql(pg_str, create_geom_google)

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

    execute_sql(pg_str, join_hotspots_query)

    google_hotspots = pd.read_sql(sql="SELECT * FROM google_all_hotspots", con=conn)

    # historical weekpatroon
    # first calculate the average weekpatroon per location
    google_week_location = google_hotspots.groupby([
        'hour', 'Hotspot', 'name'])['historical'].mean().reset_index()

    # and then calculate the average weekpatroon per vollcode
    google_week_hotspot = google_week_location.groupby([
        'Hotspot', 'hour'])['historical'].mean().reset_index()

    google_week_hotspots = google_week_hotspot.merge(google_hotspots[['Hotspot', 'Latitude', 'Longitude']]
                                                     .drop_duplicates(),
                                                     on='Hotspot')

    google_week_hotspots.rename(columns={'historical': 'drukteindex'}, inplace=True)
    google_week_hotspots.to_sql(name='drukteindex_hotspots', con=conn, if_exists='replace')
    execute_sql(pg_str, set_primary_key('drukteindex_hotspots'))
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