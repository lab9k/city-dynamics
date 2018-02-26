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
# TODO: deze lijsten variabelen on-the-fly binnenhalen uit de database
vollcodes_list = ['A07', 'F77', 'K53', 'F87', 'K24', 'K44', 'K47', 'M27',
                  'M28', 'M30', 'N64', 'N66', 'M33', 'N60', 'N61', 'N62',
                  'N73', 'T93', 'T98', 'K52', 'M29', 'M34', 'A08', 'A09',
                  'B10', 'F84', 'K59', 'N71', 'N72', 'T95', 'T96', 'E14',
                  'E17', 'A00', 'A05', 'A03', 'E41', 'E42', 'A04', 'E21',
                  'E43', 'F76', 'F78', 'F79', 'F81', 'F82', 'F83', 'E20',
                  'F86', 'E18', 'E19', 'E22', 'K25', 'K45', 'K46', 'N63',
                  'K49', 'K54', 'T92', 'M31', 'T97', 'M32', 'A01', 'M56',
                  'M57', 'A02', 'N65', 'F80', 'K48', 'F88', 'E16', 'K23',
                  'F89', 'A06', 'E40', 'K90', 'E12', 'K91', 'E36', 'E13',
                  'E15', 'M50', 'E37', 'E38', 'K26', 'E39', 'E75', 'F11',
                  'N68', 'M35', 'M51', 'M55', 'F85', 'M58', 'N67', 'N69',
                  'N70', 'N74', 'T94']

vollcodes_m2 = {'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0, 'A04': 370827.0, 'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0, 'A08': 288812.0, 'A09': 429920.0, 'B10': 9365503.0, 'E12': 218000.0, 'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0, 'E16': 173372.0, 'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0, 'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0, 'E38': 193750.0, 'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0, 'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0, 'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0, 'F78': 567032.0, 'F79': 737444.0, 'F80': 5695263.0, 'F81': 678581.0, 'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0, 'F85': 622215.0, 'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0, 'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0, 'K44': 321894.0, 'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0, 'K48': 464700.0, 'K49': 419051.0, 'K52': 462443.0, 'K53': 125127.0, 'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0, 'K91': 1018235.0, 'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0, 'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0, 'M35': 1524659.0, 'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0, 'M57': 1777311.0, 'M58': 1553531.0, 'N60': 604294.0, 'N61': 489380.0, 'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0, 'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0, 'N70': 680151.0, 'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0, 'N74': 391998.0, 'T92': 691673.0, 'T93': 1310109.0, 'T94': 1817539.0, 'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0, 'T98': 2310156.0}

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

## ALL FUNCTIONS WITH '_OLD' can be removed as soon as Tim is ready for the new API
def run_imports_old():

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
    start = np.min(alp_live.data.timestamp)
    end = np.max(alp_live.data.timestamp)
    drukte = init_drukte_df(start, end, vollcodes_list)

    # merge datasets
    cols = ['timestamp', 'vollcode', 'alpha_live']
    drukte = pd.merge(
        drukte, alp_live.data[cols], on=['timestamp', 'vollcode'], how='left')

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

    # Middel alpha expected en alpha live
    drukte['alpha'] = drukte[['alpha_week', 'alpha_live']].mean(axis=1)

    # Middel gvb
    drukte['gvb'] = drukte[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # init drukte index
    drukte['drukte_index'] = np.nan

    return drukte

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
    drukte = init_drukte_df(start, end, vollcodes_list)

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

    return drukte

##############################################################################
def linear_model(drukte):

    # Normalise verblijversindex en gvb
    drukte['verblijvers_ha_2016'] = process.norm(drukte.verblijvers_ha_2016)
    drukte['gvb'] = process.norm(drukte.gvb)

    # make sure the sum of the weights != 0
    linear_weigths = {'verblijvers_ha_2016': 1,
                      'gvb': 8,
                      'alpha_week': 2}

    lw_normalize = sum(linear_weigths.values())

    for col, weight in linear_weigths.items():
        if col in drukte.columns:
            drukte['drukte_index'] = drukte['drukte_index'].add(drukte[col] * weight, fill_value=0)

    drukte['drukte_index'] = drukte['drukte_index'] / lw_normalize

    # Sort values
    drukte = drukte.sort_values(['vollcode', 'weekday', 'hour'])

    return drukte

##############################################################################
def pipeline_base(drukte):
    """ Create base column values of ."""

    # Fill base dataframe based on linear combination of absolute datasources
    linear_weigths = {'verblijversindex': 2, 'gvb': 1}
    for col, weight in linear_weigths.items():
        if col in drukte.columns:
            base_name = 'base_' + col
            drukte[base_name] = np.nan
            drukte[base_name] = drukte[base_name].add(drukte[col] * weight, fill_value=0)
            drukte[base_name] /= sum(linear_weigths.values())

    # Normalize base
    # drukte['base'] /= sum(linear_weigths.values())

    return drukte

##############################################################################
def pipeline_mod(drukte):

    # Initialze mod values column
    drukte['mod'] = np.nan

##############################################################################
def pipeline_scale(drukte):
    pass

##############################################################################
def pipeline_model(drukte):
    """Implement pipeline model for creating the Drukte Index"""

    # Linear weights for the creation of the base value
    base_list = {'verblijvers_ha_2016': 1, 'gvb': 4}

    # Modification mappings defining what flex is used for each dataset
    mod_list = {'verblijvers_ha_2016': 'alpha'}

    # Specify view to choose scaling method (options: 'toerist', 'ois', 'politie')
    view = 'toerist'


    #### (1) Calculate base values  (use absolute sources)
    for base, weight in base_list.items():
        if base in drukte.columns:

            # Initialize base and result columns
            base_name = 'base_' + base
            drukte[base_name] = np.nan

            # Compute weighted base value
            drukte[base_name] = drukte[base_name].add(drukte[base] * weight, fill_value=0)
            drukte[base_name] /= sum(base_list.values())  # Normalize base weights


    #### (2) Modify base values  (use relative sources)
    # We assume a value of 1 in the Alpha dataset (the maximum value) implies that
    # the base value should be multiplied/flexed with the factor given below.
    factor = 4
    for base, mod in mod_list.items():
        base_name = 'base_' + base
        if base_name in drukte.columns:
            drukte['drukteindex'] += drukte[base_name] * (drukte[mod] * factor)


    #### (3) Normalize on acreage
    # TODO: Willen we gvb acreage al bij het importen normaliseren? Of niet?
    # TODO: Hier wellicht normaliseren

    #### (4) Scale
    # TODO: Data scalen tussen 0 en 1 voor front end (toerist view)


    '''
    # Create a base crowdedness value (absolute values)
    drukte = pipeline_base(drukte)

    # Modify base value with relative components to create a proxy crowdedness value
    # (estimating: #people/m^2)
    drukte = pipeline_mod(drukte)

    # Scale proxy value to create a certain view (e.g 'Toerist', 'OIS', 'Politie', etc..)
    drukte = pipeline_scale(drukte)

    # Return dataframe
    return drukte
    '''

##############################################################################
def write_to_db_old(drukte):
    """Write data to database."""
    log.debug('Writing data to database.')
    dbconfig = args.dbConfig[0]
    connection = process.connect_database(dbconfig)
    drukte.to_sql(
        name='drukteindex', con=connection, index=True, if_exists='replace')
    connection.execute('ALTER TABLE "drukteindex" ADD PRIMARY KEY ("index")')
    log.debug('done.')

def write_to_db(drukte):
    """Write data to database."""
    log.debug('Writing data to database.')
    dbconfig = args.dbConfig[0]
    connection = process.connect_database(dbconfig)
    drukte.to_sql(
        name='drukteindex_hour_week', con=connection, index=True, if_exists='replace')
    connection.execute('ALTER TABLE "drukteindex_hour_week" ADD PRIMARY KEY ("index")')
    log.debug('done.')

##############################################################################
def run_old():
    """Run the main process of this file: loading and combining all datasets."""
    drukte = run_imports_old()
    drukte = linear_model(drukte)
    # drukte = pipeline_model(drukte)
    write_to_db(drukte)

def run():
    """Run the main process of this file: loading and combining all datasets."""
    drukte = run_imports()
    drukte = linear_model(drukte)
    # drukte = pipeline_model(drukte)
    write_to_db(drukte)

##############################################################################
# Simple test for this module
if __name__ == "__main__":

    desc = "Calculate index."
    log.debug(desc)
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    run_old()
    run()