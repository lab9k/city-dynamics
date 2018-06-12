"""
This module is the main module of the analyzer.

#REFACTOR: module needs refactoring.

The analyzer imports data from all data sources and combines them into
a single 'Drukte Index' value.

main.py is dependent on process.py, which streamlines the datasource import
and transformation process.

main.py is called in abalyzer/run_index.sh.
"""

##############################################################################
import configparser
import argparse
import logging
import numpy as np

import process

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Global variables
vollcodes_m2_land = {
    'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0,
    'A04': 370827.0, 'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0,
    'A08': 288812.0, 'A09': 429920.0, 'B10': 9365503.0, 'E12': 218000.0,
    'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0, 'E16': 173372.0,
    'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0,
    'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0,
    'E38': 193750.0, 'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0,
    'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0,
    'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0,
    'F78': 567032.0, 'F79': 737444.0, 'F80': 5695263.0, 'F81': 678581.0,
    'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0, 'F85': 622215.0,
    'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0,
    'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0,
    'K44': 321894.0, 'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0,
    'K48': 464700.0, 'K49': 419051.0, 'K52': 462443.0, 'K53': 125127.0,
    'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0, 'K91': 1018235.0,
    'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0,
    'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0,
    'M35': 1524659.0, 'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0,
    'M57': 1777311.0, 'M58': 1553531.0, 'N60': 604294.0, 'N61': 489380.0,
    'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0,
    'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0,
    'N70': 680151.0, 'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0,
    'N74': 391998.0, 'T92': 691673.0, 'T93': 1310109.0, 'T94': 1817539.0,
    'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0, 'T98': 2310156.0
}

# TODO: harcoded variable hierboven vervangen met code hieronder...
# TODO: ... wanneer dbconfig niet meer noodzakelijk is voor db calls:
# dbconfig = 'dev'
# temp = process.Process(dbconfig)
# temp.import_data(['VERBLIJVERSINDEX'], ['vollcode', 'oppervlakte_land_m2'])
# vollcodes_m2_land = dict(zip(list(temp.data.vollcode),
# list(temp.data.oppervlakte_land_m2)))


def linear_model(drukte):
    """A linear model computing the drukte index values."""

    # Normalize gvb data to range 0-1 to conform with Alpha data.
    drukte.normalize_acreage_city('gvb_stad')
    drukte.normalize_acreage('gvb_buurt')

    # Normalize Alpha data to range 0-1 (not sure this is a good choice)
    drukte.normalize('alpha')

    drukte.normalize('mean_occupancy')

    # Mean gvb
    drukte.data['gvb'] = drukte.data[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # Normalise verblijversindex en gvb
    drukte.data['verblijvers_ha_2016'] = process.norm(
        drukte.data.verblijvers_ha_2016)
    drukte.data['gvb'] = process.norm(drukte.data.gvb)

    # Computations on vollcode level

    # Make sure the sum of the weights != 0
    linear_weigths_vollcode = {
        'verblijvers_ha_2016': 15, 'gvb': 55, 'mean_occupancy': 30}
    lw_vollcode_normalize = sum(linear_weigths_vollcode.values())

    for col, weight in linear_weigths_vollcode.items():
        if col in drukte.data.columns:
            drukte.data['drukteindex'] = \
                drukte.data['drukteindex'].add(
                    drukte.data[col] * weight, fill_value=0)

    drukte_index = drukte.data['drukteindex']
    drukte.data['drukteindex'] = drukte_index / lw_vollcode_normalize

    # Sort values
    drukte.data = drukte.data.sort_values(['vollcode', 'weekday', 'hour'])
    ####################################

    '''
    ####################################
    #### Computations on hotspot level

    # Create hotspot data computation dataframe
    hotspot_data = copy.deepcopy(drukte.data)
    hotspot_data['drukteindex'] = 0

    # Hotspot weights
    linear_weights_hotspots = {
        'verblijvers_ha_2016': 15, 'gvb': 15, 'alpha': 70}
    lw_hotspots_normalize = sum(linear_weights_hotspots.values())

    # Select unique hotspots
    hotspot_data.drop_duplicates(subset=['hotspot', 'weekday', 'hour'])

    # Compute drukteindex value
    for col, weights in linear_weights_hotspots.items():
        if col in drukte.data.columns:
            hotspot_data['drukteindex'] = \
                hotspot_data['drukteindex'].add(
                    drukte.data[col] * weight, fill_value=0)

    # Normalize drukteindex value
    hotspot_data['drukteindex'] = \
        hotspot_data['drukteindex'] / lw_hotspots_normalize

    # Only keep necessary columns
    hotspot_data = hotspot_data[
        ['index', 'hotspot', 'hour', 'weekday', 'drukteindex']]

    # Add to dataframe
    drukte.hotspot_data = hotspot_data[
        ['hotspot', 'weekday', 'hour', 'drukteindex']]
    ####################################
    '''

    return drukte


def calculate_drukte_base_values(drukte, base_list):
    # (1) Calculate base values  (use absolute sources)
    for base, weight in base_list.items():
        if base in drukte.data.columns:
            # Initialize base and result columns
            base_name = 'base_' + base
            drukte.data[base_name] = np.nan

            # Compute weighted base value
            drukte.data[base_name] = drukte.data[base_name].add(
                drukte.data[base] * weight, fill_value=0)
            # Normalize base list weights
            drukte.data[base_name] /= sum(base_list.values())


def dosomething_with_base_values(drukte, mod_list):

    # We assume a value of 1 in the Alpha dataset (the maximum value)
    # implies that the base value should be multiplied/flexed
    # with the factor given below.
    flex_factor = 2

    for base, mod in mod_list.items():
        base_name = 'base_' + base
        mod_name = 'base_' + base + '_mod_' + mod

        watisdit = drukte.data[base_name].fillna(0)
        geenidee = drukte.data[mod].fillna(0)
        # TODO maak code leesbaar.
        drukte.data[mod_name] = watisdit * (geenidee * flex_factor)


def calculate_drukte_index(drukte, mod_list, base_list):

    for base in base_list:
        if base in mod_list.keys():
            mod_name = 'base_' + base + '_mod_' + mod_list[base]
            drukte.data['drukteindex'] += drukte.data[mod_name]
        else:
            base_name = 'base_' + base
            drukte.data['drukteindex'] += drukte.data[base_name].fillna(0)


def pipeline_model(drukte):
    """Implements pipeline model for creating the Drukte Index"""

    # Compute mean value for gvb
    drukte.data['gvb'] = drukte.data[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # Normalize gvb and verblijversindex to #people/m2
    drukte.normalize_acreage('gvb')
    verblijvers2016 = drukte.data.verblijvers_ha_2016
    drukte.data['verblijvers_m2_2016'] = verblijvers2016 / 10000
    # 1 ha == 10000 m2
    # print(drukte.data.gvb.head())
    # print(drukte.data.verblijvers_m2_2016.head())
    # q.d()

    # Linear weights for the creation of the base value
    base_list = {'verblijvers_ha_2016': 5, 'gvb': 1}
    # base_list = {'verblijvers_ha_2016': 2, 'gvb_buurt': 8, 'gvb_stad': 1}

    # Modification mappings defining what flex is used for each dataset
    mod_list = {'verblijvers_ha_2016': 'alpha'}
    # Specify view to choose scaling method (
    # options: 'toerist', 'ois', 'politie')
    view = 'toerist'

    calculate_drukte_base_values(drukte, base_list)

    # (2) Modify base values (relative sources)
    dosomething_with_base_values(drukte, mod_list)

    # Compute drukte index values
    calculate_drukte_index(drukte, mod_list, base_list)
    # (3) Normalize on acreage
    drukte.normalize_acreage('drukteindex')

    # (4) Scale data for specific group of viewers
    if view == 'toerist':
        drukte.normalize('drukteindex')

    return drukte


##############################################################################
def write_table_to_db(dataframe, table_name):
    """Write dataframe to database table with given name.

    If table already exists, replace it.
    """
    log.debug('creating or replacing table \"%s\".' % table_name)
    dbconfig = args.dbConfig[0]
    connection = process.connect_database(dbconfig)

    # Write dataframe data to table
    dataframe.to_sql(
        name=table_name, con=connection, index=True, if_exists='replace')
    connection.execute(f'ALTER TABLE "{table_name}" ADD PRIMARY KEY ("index")')

    log.debug('done.')


##############################################################################
def fill_table_in_db(org_table_name, fill_table_name, columns):
    """Insert data from selected columns into an existing table in database."""

    # REMOVE DEAD CODE !!!
    # TODO: First test this via DBeaver. column names between org_table
    # and fill_table will be different due to the foreign key constraint #noqa
    #
    # """
    # log.debug(
    #     f'Inserting data "{org_table_name}" into "{fill_table_name}\"')
    # dbconfig = args.dbConfig[0]
    # connection = process.connect_database(dbconfig)
    #
    # # Truncate data from the table that has to be filled
    # connection.execute("TRUNCATE TABLE %s" % fill_table_name)
    #
    # # Create data insertion statement
    # insert = "INSERT INTO {0}(".format(fill_table_name)
    # for i in range(0, len(columns)):
    #     insert += str(columns[i])
    #     if i < len(columns)-1:
    #         insert += ", "
    # insert += ") SELECT "
    # for i in range(0, len(columns)):
    #     insert += str(columns[i])
    #     if i < len(columns)-1:
    #         insert += ", "
    # insert += ' FROM {0};'.format(org_table_name)
    #
    # log.debug(insert)
    # q.d()
    #
    # # Insert data into table
    # connection.execute(insert)
    #
    # log.debug('done.')"""
    #
    # """

    dbconfig = args.dbConfig[0]
    connection = process.connect_database(dbconfig)
    # datasets_buurtcombinatiedrukteindex
    insert_into_api_table = """
    TRUNCATE TABLE "datasets_buurtcombinatiedrukteindex";
    insert into "datasets_buurtcombinatiedrukteindex" (
    index,
    hour,
    weekday,
    drukteindex,
    vollcode_id
    ) SELECT
      c.index,
      hour,
      weekday,
      drukteindex,
      b.ogc_fid from buurtcombinatie b,
      drukteindex_buurtcombinaties c
    where  b."vollcode" = c."vollcode";

    """
    connection.execute(insert_into_api_table)

    log.debug('done.')


def run():
    """loading and combining all datasets."""
    # dbconfig is the same for all datasources now.
    # Could be different in the future.
    dbconfig = args.dbConfig[0]
    drukte = process.Process_drukte(dbconfig)

    # Still use older linear model for now
    pipeline_on = False

    if pipeline_on is True:
        drukte = pipeline_model(drukte)

    if pipeline_on is False:
        drukte = linear_model(drukte)

    '''
    if pipeline_on == False:
        drukte = linear_model(drukte)

        # Write complete hotspot data (all columns) to table.
        write_table_to_db(drukte.hotspot_data, 'drukteindex_hotspots')

        # Fill specific hotspot table for API (selection of columns).
        fill_table_in_db('drukteindex_hotspots', 'datasets_hotspotsdrukteindex',
            ['index', 'hotspot', 'hotspot_id', 'hour', 'weekday', 'drukteindex'])
    '''  # noqa

    # Write complete buurtcombinatie data (all columns) to table.
    write_table_to_db(drukte.data, 'drukteindex_buurtcombinaties')

    # # TODO: find a way in Django to enhance a model with
    # columns from another table. Currently only foreign key
    # # Fill specific buurtcombinatie table for API (selection of columns).
    # fill_table_in_db('drukteindex_buurtcombinaties',
    #   'datasets_buurtcombinatiedrukteindex',
    #     ['index', 'vollcode',
    #      'vollcode_id', 'hour', 'weekday', 'drukteindex'])

    fill_table_in_db(
        'drukteindex_buurtcombinaties',
        'datasets_buurtcombinatiedrukteindex',
        ['index', 'ogc_fid', 'hour', 'weekday', 'drukteindex'])


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
