"""
This module is a fallback version of process.py.

#REMOVE (marked for future removal)

This module is not in use anymore. It implements an older version of class 'Process'.
The functionality of this script is now replaced by main.py and process.py.

ORIGINAL DESCRIPTION:
For each dataset, a subclass of class 'Process' is created to load and pre-process this dataset.
# Implemented methods of class 'Process':
* def database_connection()
* def import()
* def normalize()
* def min-max()
* def rename()  # Optional: to rename columns
# Children of class 'Process':
* Class Process_gvb(Process)
* Class Process_google(Process)
* Class Process_verblijversindex(Process)
* Class Process_tellus(Process)
* Etc..
"""

##############################################################################
import configparser
import argparse
import logging
import numpy as np
import pandas as pd
import q

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sklearn import preprocessing
from datetime import timedelta

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Global variables
# TODO: onderstaande twee lijsten on-the-fly als globals binnenhalen uit de database.
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

vollcodes_land_m2 = {'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0, 'A04': 370827.0, 'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0, 'A08': 288812.0, 'A09': 429920.0, 'B10': 9365503.0, 'E12': 218000.0, 'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0, 'E16': 173372.0, 'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0, 'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0, 'E38': 193750.0, 'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0, 'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0, 'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0, 'F78': 567032.0, 'F79': 737444.0, 'F80': 5695263.0, 'F81': 678581.0, 'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0, 'F85': 622215.0, 'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0, 'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0, 'K44': 321894.0, 'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0, 'K48': 464700.0, 'K49': 419051.0, 'K52': 462443.0, 'K53': 125127.0, 'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0, 'K91': 1018235.0, 'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0, 'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0, 'M35': 1524659.0, 'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0, 'M57': 1777311.0, 'M58': 1553531.0, 'N60': 604294.0, 'N61': 489380.0, 'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0, 'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0, 'N70': 680151.0, 'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0, 'N74': 391998.0, 'T92': 691673.0, 'T93': 1310109.0, 'T94': 1817539.0, 'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0, 'T98': 2310156.0}


##############################################################################
# Helper Functions

def connect_database(dbconfig):
    """Create connection with a database."""
    postgres_url = URL(
        drivername='postgresql',
        host=config_auth.get(dbconfig, 'host'),
        port=config_auth.get(dbconfig, 'port'),
        database=config_auth.get(dbconfig, 'dbname'),
        username=config_auth.get(dbconfig, 'user'),
        password=config_auth.get(dbconfig, 'password')
    )
    return create_engine(postgres_url)

def norm(x):
    """Scale numeric array to [0, 1]."""
    x = np.array(x)
    x = (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
    return x

##############################################################################
class Process():
    """This class implements the process of loading and pre-processing all data from one datasource."""

    def __init__(self, dbconfig):
        """Initialize a Process instance."""
        self.name = ''                                  # Name of datasource
        self.data = pd.DataFrame()                      # Data of datasource
        self.pattern = pd.DataFrame()                   # Patterns of datasource
        self.conn = connect_database(dbconfig)          # Database connection of datasource

    def __str__(self):
        """Print string representation of Process"""
        return "Dataset name: %s\nData: %s" % (self.name, self.data)


    def import_data(self, tables, columns):
        """Import the datasource's data from the storage database as a Pandas dataframe."""
        d = dict.fromkeys(tables)
        for table in tables:
            d[table] = self.import_table(table)             # Import each table as dataframe
            if columns == []:
                pass
            else:
                d[table] = d[table][columns]                # Only select relevant columns
        self.data = pd.concat([v for v in d.values()])      # Combine dataframes
        del d
        self.process_timestamps()


    def import_table(self, table):
        """Import one table from the database (one datasource could be split up into multiple tables)."""
        sql_query = """ SELECT * FROM "{}" """  # Standard format sql query
        table_data = pd.read_sql(sql=sql_query.format(table), con=self.conn)
        return table_data


    def process_timestamps(self):
        """Create weekday and hour columns when a timestamp column exists"""
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = self.data.timestamp.dt.round('60min')
            self.data['weekday'] = [ts.weekday() for ts in self.data.timestamp]
            self.data['hour'] = [ts.hour for ts in self.data.timestamp]


    def dataset_specific(self):
        """To be implemented by child classes"""
        pass


    def rename(self, cols_rename):
        """Rename specific columns to handle naming conventions differences between datasets."""
        self.data.rename(columns=cols_rename, inplace=True)


    def normalize(self, cols_norm):
        """Normalize all specified columns"""
        if cols_norm != []:                 # Check if any columns should be normalized at all.
            if type(cols_norm) == str:      # Check whether we have a single column name string,
                cols_norm = [cols_norm]     # if so, wrap this single name in a list.
            for col in cols_norm:           # Now process the list of 1+ column names :)
                self.data[col] = norm(self.data[col])


    def normalize_acreage(self, cols):
        """Normalize all specified columns based on the surface area."""
        # In onderstaande stappen kunnen momenteel locaties wegvallen welke geen vollcode
        # bevatten die in de verblijversindex voorkomt (dit is bijv. het geval met de gvb data).
        if cols != []:                  # Check if any columns should be normalized at all.
            if type(cols) == str:       # Check whether we have a single column name string,
                cols = [cols]           # if so, wrap this single name in a list.
            for col in cols:            # Now process the list of 1+ column names.
                m2 = pd.DataFrame(list(vollcodes_land_m2.items()), columns=['vollcode','oppervlakte_land_m2'])
                temp = self.data.merge(m2)
                temp.gvb_buurt = temp.gvb_buurt / temp.oppervlakte_land_m2  # Normalize based on surface area
                temp.drop('oppervlakte_land_m2', axis=1, inplace=True)
                self.data = temp


    def normalize_acreage_city(self, col):
        """Normalize on acreage on city wide """
        total_m2_stad = sum(vollcodes_land_m2.values())
        self.data[col] = self.data[col] / total_m2_stad


    def aggregate_on_column(self, col):
        """Aggregate the dataframe in self.data on the given column."""
        # TODO: (4) Implement aggregate on column method.
        pass


    def create_pattern(self, time_period, area_precision):
        """Create a crowdedness pattern.
        # TODO: Implement pattern creation method
        Keyword arguments:
        time_period - the period for which we create the pattern (e.g. 'day', 'week', 'year')
        area_precision - the "area" precision of the pattern (e.g. 'lat/long', 'vollcode', 'stadsdeelcode', 'stad')
        """
        pass


    # def create_pattern_week_lat_long(self):
    #     area_mapping = self.data[['vollcode', 'stadsdeelcode']].drop_duplicates()
    #     # first calculate the average weekpatroon per location
    #     google_week_location = self.data.groupby([
    #         'weekday', 'hour', 'vollcode', 'name'])['historical'].mean().reset_index()
    #     google_week_location = google_week_location.merge(area_mapping, on='vollcode')
    #
    #
    # def create_pattern_week_vollcode(self):
    #     # and then calculate the average weekpatroon per vollcode
    #     google_week_vollcode = google_week_location.groupby([
    #         'vollcode', 'weekday', 'hour'])['historical'].mean().reset_index()
    #
    #     # also calculate the average weekpatroon per stadsdeel
    #     google_week_stadsdeel = google_week_location.groupby([
    #         'stadsdeelcode', 'weekday', 'hour'])['historical'].mean().reset_index()

##############################################################################
class Process_gvb_stad(Process):
    """This class implements all data importing and pre-processing steps, specifically for the GVB datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'gvb_stad'
        self.import_data(['gvb_with_bc'],
                         ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])
        self.dataset_specific()
        self.rename({'incoming': 'gvb_stad'})
        self.normalize_acreage_city('gvb_stad')


    def dataset_specific(self):
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = self.data.halte.isin(haltes)

        # Stadsniveau (sum of incoming values over all areas)
        gvb_stad = self.data.loc[indx, :]
        gvb_stad = gvb_stad.groupby(['weekday', 'hour'])['incoming'].sum()
        self.data = gvb_stad.reset_index()

##############################################################################
class Process_gvb_buurt(Process):
    """This class implements all data importing and pre-processing steps, specifically for the GVB datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'gvb_buurt'
        self.import_data(['gvb_with_bc'],
                         ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])
        self.dataset_specific()
        self.rename({'incoming': 'gvb_buurt'})
        self.normalize_acreage('gvb_buurt')


    def dataset_specific(self):
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = self.data.halte.isin(haltes)

        # Buurtniveau
        gvb_buurt = self.data.loc[np.logical_not(indx), :]
        self.data = gvb_buurt.groupby(['vollcode', 'weekday', 'hour'])['incoming'].mean().reset_index()

##############################################################################
class Process_alpha_historical(Process):
    """This class implements all data importing and pre-processing steps for the alpha datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'alpha_historical_week'
        self.import_data(['google_with_b', 'google_dec_with_bc'],
                         ['name', 'vollcode', 'timestamp', 'historical', 'stadsdeel_code'])
        self.dataset_specific()
        self.rename({'historical': 'alpha_week'})
        self.normalize('alpha_week')


    def dataset_specific(self):
        area_mapping = self.data[['vollcode', 'stadsdeel_code']].drop_duplicates()

        # historical weekpatroon
        # first calculate the average weekpatroon per location
        google_week_location = self.data.groupby([
            'weekday', 'hour', 'vollcode', 'name'])['historical'].mean().reset_index()
        google_week_location = google_week_location.merge(area_mapping, on='vollcode')

        # and then calculate the average weekpatroon per vollcode
        google_week_vollcode = google_week_location.groupby([
            'vollcode', 'weekday', 'hour'])['historical'].mean().reset_index()

        # also calculate the average weekpatroon per stadsdeel
        google_week_stadsdeel = google_week_location.groupby([
            'stadsdeel_code', 'weekday', 'hour'])['historical'].mean().reset_index()

        # set arbitrary threshold on how many out of 168 hours in a week need to contain measurements, per vollcode.
        # in case of sparse data, take the stadsdeelcode aggregation
        minimal_hours = 98
        cnt = google_week_vollcode.vollcode.value_counts()
        sparse_vollcodes = cnt[cnt < minimal_hours].index.tolist()

        # first take the vollcode aggregation for vollcodes that have enough data
        google_week_vollcode = google_week_vollcode[~google_week_vollcode.vollcode.isin(sparse_vollcodes)]

        # then take the staddeelcode aggregation for vollcodes for which data is sparse
        google_week_stadsdeel = google_week_stadsdeel.merge(area_mapping, on='stadsdeel_code')
        google_week_stadsdeel.drop('stadsdeel_code', axis=1, inplace=True)
        google_week_stadsdeel = google_week_stadsdeel[google_week_stadsdeel.vollcode.isin(sparse_vollcodes)]

        self.data = pd.concat([google_week_vollcode, google_week_stadsdeel])

##############################################################################
class Process_alpha_live(Process):
    """This class implements all data importing and pre-processing steps for the alpha datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'alpha_live'
        self.import_data(['google_with_bc', 'google_dec_with_bc'],
                         ['name', 'vollcode', 'timestamp', 'live', 'stadsdeel_code'])
        self.dataset_specific()
        self.rename({'live': 'alpha_live'})
        self.normalize('alpha_live')


    def dataset_specific(self):
        self.data = self.data.loc[self.data.live.notnull(), :]
        self.data = self.data.groupby(['vollcode', 'timestamp'])['live'].mean()
        self.data = self.data.reset_index()
        self.data['weekday'] = [ts.weekday() for ts in self.data.timestamp]
        self.data['hour'] = [ts.hour for ts in self.data.timestamp]

##############################################################################
class Process_verblijversindex(Process):
    """This class implements all data importing and pre-processing steps for the verblijversindex datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'verblijversindex'
        self.import_data(['VERBLIJVERSINDEX'],
                         ['vollcode', 'inwoners', 'werkzame_personen', 'studenten',
                          'bezoekers', 'verblijvers', 'oppervlakte_land_m2',
                          'oppervlakte_land_water_m2', 'verblijvers_ha_2016'])

##############################################################################
class Process_tellus(Process):
    """This class implements all data importing and pre-processing steps for the tellus datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'tellus'
        self.import_data(['tellus_with_bc'],
                         ['tellus', 'timestamp', 'vollcode'])
        self.dataset_specific()
        self.normalize('tellus')

##############################################################################
class Process_buurtcombinatie(Process):

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'bc_codes'
        self.import_data(['buurtcombinatie'], ['vollcode'])