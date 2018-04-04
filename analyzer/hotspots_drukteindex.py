"""
This module computes the drukteindex values for ~40 hand-picked hotspots.
"""

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


def linear_model(drukte):
    """
    This linear model is copied from analyzer/main.py.

    This function is slightly adapted here (i.e. changed linear_weight values)
    in order to compute values for the hotspots which are predominantly based
    on the (relative) Alpha values of the hotspot locations.
    """

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
    """
    This is the main function of this script.

    This function processes all the hotspots: it finds all relevant locations in a 200m radius
    around each hotspot and computes a prediction value for the hotspot for each hour of the week.
    When no data is available from locations around the hotspot, the data from the vollcode area
    of the hotspot is used as fallback.
    """
    conn = get_conn()

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

    alpha_week_hotspots = alpha_week_hotspots.merge(hotspots_df[['hotspot', 'vollcode']], on='hotspot')

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
    TRUNCATE TABLE datasets_hotspotsdrukteindex;
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