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

def get_conn():
    """Create a connection to the database."""
    dbconfig = 'docker'
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


# COPIED from main.py
def linear_model(drukte):
    # Normalise verblijversindex en gvb
    # drukte['verblijvers_ha_2016'] = process.norm(drukte.verblijvers_ha_2016)
    # drukte['gvb'] = process.norm(drukte.gvb)

    drukte['drukte_index'] = 0

    # Make sure the sum of the weights != 0
    linear_weigths = {'verblijvers_ha_2016': 15, 'gvb': 15, 'alpha': 70}
    lw_normalize = sum(linear_weigths.values())

    for col, weight in linear_weigths.items():
        if col in drukte.columns:
            drukte['drukte_index'] = drukte['drukte_index'].add(drukte[col] * weight, fill_value=0)

    drukte['drukte_index'] = drukte['drukte_index'] / lw_normalize

    # Sort values
    drukte = drukte.sort_values(['vollcode', 'weekday', 'hour'])

    def norm(x):
        """Scale numeric array to [0, 1]."""
        x = np.array(x)
        x = (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
        return x

    drukte['drukte_index'] = norm(drukte['drukte_index'])

    return drukte


def main():
    conn = get_conn()

    #TODO: HACK. Make this work for existing geometries in the importer!
    q1 = """
    ALTER TABLE hotspots
    DROP COLUMN IF EXISTS point_sm;
    """

    q2 = """
    ALTER TABLE hotspots
    ADD COLUMN point_sm geometry;
    UPDATE hotspots SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "lon", "lat"), 4326), 3857);
    """
    q3 = """
    ALTER TABLE "alpha_locations_expected"
    DROP COLUMN IF EXISTS point_sm;
    """

    q4 = """
    ALTER TABLE alpha_locations_expected
    ADD COLUMN point_sm geometry;
    UPDATE alpha_locations_expected SET point_sm = ST_TRANSFORM( ST_SETSRID ( ST_POINT( "lon", "lat"), 4326), 3857);
    """

    q5 = """
    UPDATE alpha_locations_expected SET hotspot = hotspots."hotspot"
    FROM hotspots 
    WHERE st_intersects(
    alpha_locations_expected.point_sm,
    ST_BUFFER(hotspots.point_sm, 100));
    """

    q6 = """
    ALTER TABLE "alpha_locations_expected"
    DROP COLUMN IF EXISTS point_sm;
    """

    conn.execute(q1)
    conn.execute(q2)
    conn.execute(q3)
    conn.execute(q4)
    conn.execute(q5)
    conn.execute(q6)


    alpha_hotspots = pd.read_sql(sql="SELECT * FROM alpha_locations_expected", con=conn)

    hotspots_df = pd.read_sql("""SELECT * FROM hotspots""", conn)

    # historical weekpatroon
    # first calculate the average weekpatroon per location
    alpha_week_location = alpha_hotspots.groupby([
        'hour', 'hotspot', 'name'])['expected'].mean().reset_index()

    # and then calculate the average weekpatroon per hotspot
    alpha_week_hotspots = alpha_week_location.groupby([
        'hotspot', 'hour'])['expected'].mean().reset_index()

    alpha_week_hotspots.rename(columns={'expected': 'alpha_week'}, inplace=True)

    # fill the dataframe with all missing hotspot-hour combinations
    x = {"weekday": np.arange(7), "hour": np.arange(24), "hotspot": hotspots_df['hotspot'].unique().tolist()}
    hs_hour_combinations = pd.DataFrame(list(itertools.product(*x.values())), columns=x.keys())
    alpha_week_hotspots = alpha_week_hotspots.merge(hs_hour_combinations, on=['hour', 'hotspot'], how='outer')
    alpha_week_hotspots['alpha_week'].fillna(value=0, inplace=True)

    alpha_week_hotspots = alpha_week_hotspots.merge(alpha_hotspots[['hotspot', 'vollcode']]
                                                      .drop_duplicates('hotspot'), on='hotspot')

    di = pd.read_sql(sql="SELECT * FROM drukteindex_buurtcombinaties", con=conn)

    drukteindex_hotspots = alpha_week_hotspots.merge(di[['index',
                                                          'vollcode',
                                                          'weekday',
                                                          'hour',
                                                          'verblijvers_ha_2016',
                                                          'gvb']], on=['vollcode', 'weekday', 'hour'], how='left')

    drukteindex_hotspots = linear_model(drukteindex_hotspots)

    drukteindex_hotspots = drukteindex_hotspots[['hotspot', 'hour', 'weekday', 'drukte_index']]

    drukteindex_hotspots.rename(columns={'drukte_index': 'drukteindex'}, inplace=True)

    log.debug('Writing to db..')
    drukteindex_hotspots.to_sql(name='drukteindex_hotspots', con=conn, if_exists='replace')

    insert_into_models_hotspots = """
    insert into datasets_hotspotsdrukteindex (
    index,
    hour,
    weekday,
    drukteindex,
    hotspot_id
    ) select c.index, hour, weekday, drukteindex, h.index from hotspots h, drukteindex_hotspots c
    where  h."hotspot" = c."hotspot";

    """

    conn.execute(insert_into_models_hotspots)

    log.debug('done.')


if __name__ == '__main__':
    desc = "Calculate index hotspots."
    log.debug(desc)
    main()