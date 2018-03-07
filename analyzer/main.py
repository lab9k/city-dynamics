"""
This module is the main module of the analyzer.

The analyzer imports data from all data sources and combines them into
a single 'Drukte Index' value.
"""

##############################################################################
import configparser
import argparse
import logging
import numpy as np
import pandas as pd
import datetime
import q

import process

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sklearn import preprocessing
from datetime import timedelta

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Global variables
vollcodes_m2_land = {'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0, 'A04': 370827.0,
                     'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0, 'A08': 288812.0, 'A09': 429920.0,
                     'B10': 9365503.0, 'E12': 218000.0, 'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0,
                     'E16': 173372.0, 'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0,
                     'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0, 'E38': 193750.0,
                     'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0, 'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0,
                     'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0, 'F78': 567032.0, 'F79': 737444.0,
                     'F80': 5695263.0, 'F81': 678581.0, 'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0,
                     'F85': 622215.0, 'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0,
                     'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0, 'K44': 321894.0,
                     'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0, 'K48': 464700.0, 'K49': 419051.0,
                     'K52': 462443.0, 'K53': 125127.0, 'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0,
                     'K91': 1018235.0, 'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0,
                     'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0, 'M35': 1524659.0,
                     'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0, 'M57': 1777311.0, 'M58': 1553531.0,
                     'N60': 604294.0, 'N61': 489380.0, 'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0,
                     'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0, 'N70': 680151.0,
                     'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0, 'N74': 391998.0, 'T92': 691673.0,
                     'T93': 1310109.0, 'T94': 1817539.0, 'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0,
                     'T98': 2310156.0}

# TODO: harcoded variable hierboven vervangen met code hieronder...
# TODO: ... wanneer dbconfig niet meer noodzakelijk is voor db calls:
# dbconfig = 'dev'
# temp = process.Process(dbconfig)
# temp.import_data(['VERBLIJVERSINDEX'], ['vollcode', 'oppervlakte_land_m2'])
# vollcodes_m2_land = dict(zip(list(temp.data.vollcode), list(temp.data.oppervlakte_land_m2)))

##############################################################################
def init_drukte_df(start_datetime, end_datetime, vollcodes):
    timestamps = pd.date_range(start=start_datetime, end=end_datetime, freq='H')
    ts_vc = [(ts, vc) for ts in timestamps for vc in vollcodes]
    drukte = pd.DataFrame({
        'timestamp': [x[0] for x in ts_vc],
        'vollcode': [x[1] for x in ts_vc]
    }).sort_values(['timestamp', 'vollcode'])
    drukte['weekday'] = [ts.weekday() for ts in drukte.timestamp]
    drukte['hour'] = [ts.hour for ts in drukte.timestamp]
    return drukte


##############################################################################
def run_imports():
    # Import datasets
    dbconfig = args.dbConfig[0]  # dbconfig is the same for all datasources now. Could be different in the future.
    brt = process.Process_buurtcombinatie(dbconfig)
    vbi = process.Process_verblijversindex(dbconfig)
    gvb_st = process.Process_gvb_stad(dbconfig)
    gvb_bc = process.Process_gvb_buurt(dbconfig)
    # tel = process.Process_tellus(dbconfig)
    alp_hist = process.Process_alpha_historical(dbconfig)
    alp_live = process.Process_alpha_live(dbconfig)

    # initialize drukte dataframe
    start = datetime.datetime(2018, 2, 12, 0, 0)  # Start of a week: Monday at midnight
    end = datetime.datetime(2018, 2, 18, 23, 0)  # End of this week: Sunday 1 hour before midnight
    drukte = init_drukte_df(start, end, list(vollcodes_m2_land.keys()))

    # merge datasets
    cols = ['vollcode', 'weekday', 'hour', 'alpha_week']
    drukte = pd.merge(
        drukte, alp_hist.data[cols],
        on=['weekday', 'hour', 'vollcode'], how='left')

    drukte = pd.merge(
        drukte, gvb_bc.data,
        on=['vollcode', 'weekday', 'hour'], how='left')

    drukte = pd.merge(
        drukte, gvb_st.data,
        on=['weekday', 'hour'], how='left')

    drukte = pd.merge(
        drukte, vbi.data,
        on='vollcode', how='left')

    # # Middel alpha expected en alpha live
    # drukte['alpha'] = drukte[['alpha_week', 'alpha_live']].mean(axis=1)

    # HACK: alpha_live not available, so just take alpha_week
    drukte['alpha'] = drukte[['alpha_week']].mean(axis=1)

    # Middel gvb
    drukte['gvb'] = drukte[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # init drukte index
    drukte['drukte_index'] = 0

    # Remove timestamps from weekpattern (only day and hour are relevant)
    drukte.drop('timestamp', axis=1, inplace=True)


##############################################################################
def linear_model(drukte):
    """A linear model computing the drukte index values."""

    # Normalize gvb data to range 0-1 to conform with Alpha data.
    drukte.normalize_acreage_city('gvb_stad')
    drukte.normalize_acreage('gvb_buurt')

    # Normalize Alpha data to range 0-1 (not sure this is a good choice)
    drukte.normalize('alpha_week')

    # Mean gvb
    drukte.data['gvb'] = drukte.data[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # Normalise verblijversindex en gvb
    drukte.data['verblijvers_ha_2016'] = process.norm(drukte.data.verblijvers_ha_2016)
    drukte.data['gvb'] = process.norm(drukte.data.gvb)

    # Make sure the sum of the weights != 0
    linear_weigths = {'verblijvers_ha_2016': 1,
                      'gvb': 8,
                      'alpha_week': 2}

    lw_normalize = sum(linear_weigths.values())

    for col, weight in linear_weigths.items():
        if col in drukte.data.columns:
            drukte.data['drukte_index'] = drukte.data['drukte_index'].add(drukte.data[col] * weight, fill_value=0)

    drukte.data['drukte_index'] = drukte.data['drukte_index'] / lw_normalize

    # Sort values
    drukte.data = drukte.data.sort_values(['vollcode', 'weekday', 'hour'])

    return drukte


##############################################################################
def pipeline_model(drukte):
    """Implement pipeline model for creating the Drukte Index"""

    # Compute mean value for gvb
    drukte.data['gvb'] = drukte.data[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # Normalize gvb and verblijversindex to #people/m2
    drukte.normalize_acreage('gvb')
    drukte.data['verblijvers_m2_2016'] = drukte.data.verblijvers_ha_2016 / 10000  # 1 ha == 10000 m2
    # print(drukte.data.gvb.head())
    # print(drukte.data.verblijvers_m2_2016.head())
    # q.d()

    # Linear weights for the creation of the base value
    base_list = {'verblijvers_ha_2016': 5, 'gvb': 1}
    # base_list = {'verblijvers_ha_2016': 2, 'gvb_buurt': 8, 'gvb_stad': 1}

    # Modification mappings defining what flex is used for each dataset
    mod_list = {'verblijvers_ha_2016': 'alpha_week'}

    # We assume a value of 1 in the Alpha dataset (the maximum value) implies that
    # the base value should be multiplied/flexed with the factor given below.
    flex_factor = 2

    # Specify view to choose scaling method (options: 'toerist', 'ois', 'politie')
    view = 'toerist'

    #### (1) Calculate base values  (use absolute sources)
    for base, weight in base_list.items():
        if base in drukte.data.columns:
            # Initialize base and result columns
            base_name = 'base_' + base
            drukte.data[base_name] = np.nan

            # Compute weighted base value
            drukte.data[base_name] = drukte.data[base_name].add(drukte.data[base] * weight, fill_value=0)
            drukte.data[base_name] /= sum(base_list.values())  # Normalize base list weights

    #### (2) Modify base values (relative sources)
    for base, mod in mod_list.items():
        base_name = 'base_' + base
        mod_name = 'base_' + base + '_mod_' + mod
        drukte.data[mod_name] = drukte.data[base_name].fillna(0) * (drukte.data[mod].fillna(0) * flex_factor)

    # Compute drukte index values
    for base in base_list:
        if base in mod_list.keys():
            mod_name = 'base_' + base + '_mod_' + mod_list[base]
            drukte.data['drukte_index'] += drukte.data[mod_name]
        else:
            base_name = 'base_' + base
            drukte.data['drukte_index'] += drukte.data[base_name].fillna(0)

    # Compute the drukte_index using the base and modified values (commented out because done in previous step now.)
    # for base in base_list:
    #     base_name = 'base_' + base
    #     mod_name = 'base_' + base + '_mod_' + mod
    #     if base_name + base in drukte.data.columns:
    #         drukte.data['drukte_index'] += drukte.data[mod_name]

    #### (3) Normalize on acreage
    drukte.normalize_acreage('drukte_index')

    #### (4) Scale data for specific group of viewers
    if view == 'toerist':
        drukte.normalize('drukte_index')

    return drukte


##############################################################################
def write_to_db(drukte):
    """Write data to database."""
    log.debug('Writing data to database.')
    dbconfig = args.dbConfig[0]
    connection = process.connect_database(dbconfig)
    drukte.data.to_sql(
        name='drukteindex_hour_week', con=connection, index=True, if_exists='replace')
    connection.execute('ALTER TABLE "drukteindex_hour_week" ADD PRIMARY KEY ("index")')

    # # write relevant columns to a table which is served by an API
    # # first, create a primary key on the buurtcombinatie table. TODO: find a better place (in the importer) for this
    # connection.execute('ALTER TABLE test1 ADD COLUMN id SERIAL PRIMARY KEY;')

    insert_into_api_table = """
    insert into datasets_buurtcombinatiedrukteindex (
    index,
    hour,
    weekday,
    drukteindex,
    vollcode_id
    ) select c.index, hour, weekday, drukte_index, b.ogc_fid from buurtcombinatie b, drukteindex_hour_week c
    where  b."vollcode" = c."vollcode";

    """
    connection.execute(insert_into_api_table)
    log.debug('done.')


##############################################################################
def run():
    """Run the main process of this file: loading and combining all datasets."""
    dbconfig = args.dbConfig[0]  # dbconfig is the same for all datasources now. Could be different in the future.
    drukte = process.Process_drukte(dbconfig)
    drukte = linear_model(drukte)
    # drukte = pipeline_model(drukte)
    write_to_db(drukte)


##############################################################################
if __name__ == "__main__":
    """Run the analyzer."""
    desc = "Calculate index."
    log.debug(desc)
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    run()
