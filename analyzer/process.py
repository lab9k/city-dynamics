"""
Module implements class 'Process'.

#REFACTOR: module needs refactoring.

For each dataset, a subclass of class 'Process' is created to load and pre-process this dataset.
"""

##############################################################################
import configparser
import argparse
import logging
import datetime
import numpy as np
import pandas as pd
import q

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sklearn import preprocessing

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Global variables
vollcodes_m2_land = {'A00': 125858.0, 'A01': 334392.0, 'A02': 139566.0, 'A03': 180643.0, 'A04': 370827.0, 'A05': 229771.0, 'A06': 296826.0, 'A07': 252101.0, 'A08': 288812.0, 'A09': 429920.0, 'B10': 9365503.0, 'E12': 218000.0, 'E13': 637040.0, 'E14': 203183.0, 'E15': 240343.0, 'E16': 173372.0, 'E17': 112541.0, 'E18': 83752.0, 'E19': 114338.0, 'E20': 130217.0, 'E21': 114415.0, 'E22': 72691.0, 'E36': 925362.0, 'E37': 435193.0, 'E38': 193750.0, 'E39': 280652.0, 'E40': 105993.0, 'E41': 95942.0, 'E42': 173133.0, 'E43': 141665.0, 'E75': 87376.0, 'F11': 3905101.0, 'F76': 445519.0, 'F77': 1335095.0, 'F78': 567032.0, 'F79': 737444.0, 'F80': 5695263.0, 'F81': 678581.0, 'F82': 449585.0, 'F83': 232898.0, 'F84': 459192.0, 'F85': 622215.0, 'F86': 807666.0, 'F87': 557372.0, 'F88': 1621957.0, 'F89': 444324.0, 'K23': 1129635.0, 'K24': 308345.0, 'K25': 195632.0, 'K26': 153464.0, 'K44': 321894.0, 'K45': 91017.0, 'K46': 420005.0, 'K47': 728062.0, 'K48': 464700.0, 'K49': 419051.0, 'K52': 462443.0, 'K53': 125127.0, 'K54': 515835.0, 'K59': 115825.0, 'K90': 1973117.0, 'K91': 1018235.0, 'M27': 173249.0, 'M28': 472189.0, 'M29': 236464.0, 'M30': 148598.0, 'M31': 205950.0, 'M32': 430360.0, 'M33': 767262.0, 'M34': 3353718.0, 'M35': 1524659.0, 'M51': 686452.0, 'M55': 2509678.0, 'M56': 3825448.0, 'M57': 1777311.0, 'M58': 1553531.0, 'N60': 604294.0, 'N61': 489380.0, 'N62': 159771.0, 'N63': 64419.0, 'N64': 33674.0, 'N65': 552047.0, 'N66': 1605957.0, 'N67': 588100.0, 'N68': 702026.0, 'N69': 711440.0, 'N70': 680151.0, 'N71': 835342.0, 'N72': 81074.0, 'N73': 8639562.0, 'N74': 391998.0, 'T92': 691673.0, 'T93': 1310109.0, 'T94': 1817539.0, 'T95': 739520.0, 'T96': 807588.0, 'T97': 527617.0, 'T98': 2310156.0}

# TODO: harcoded variable hierboven vervangen met code hieronder...
# TODO: ... wanneer dbconfig niet meer noodzakelijk is voor db calls:
# dbconfig = 'dev'
# temp = process.Process(dbconfig)
# temp.import_data(['verblijversindex'], ['vollcode', 'oppervlakte_land_m2'])
# vollcodes_m2_land = dict(zip(list(temp.data.vollcode), list(temp.data.oppervlakte_land_m2)))

##############################################################################
# Helper Functions

def connect_database(dbconfig):
    """Create a sqlachemy connection with a database."""
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
    """Scale all values in a given numeric array to range [0, 1]."""
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
        self.patterns = pd.DataFrame()                  # Patterns of datasource
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
        """Normalize all specified columns. Can be given one column name as a string, or a list of column names."""
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
            # Add m2 column if not already present
            m2 = pd.DataFrame(list(vollcodes_m2_land.items()), columns=['vollcode','oppervlakte_land_m2'])
            if type(cols) == str:       # Check whether we have a single column name string,
                cols = [cols]           # if so, wrap this single name in a list.
            for col in cols:            # Now process the list of 1+ column names.
                temp = self.data.merge(m2)
                temp[col] = temp[col] / temp.oppervlakte_land_m2  # Normalize based on surface area
                self.data = temp
            # TODO: Remove column if it did not exist before calling this function
            # temp.drop('oppervlakte_land_m2', axis=1, inplace=True)


    def normalize_acreage_city(self, col):
        """Normalize all values of the given column using the total city-wide acreage."""

        # TODO: Clean up this function. Current functionality is probably what we want.
        # TODO: Other option would be to divide by city wide value, and multiply by m2 of
        # TODO: corresponding vollcode. Then the city value would be evenly spready out over
        # TODO: all buurtcombinaties, normalized by their size (but not normalized by m2).
        # Add column with oppervlakte data
        # m2 = pd.DataFrame(list(vollcodes_m2_land.items()), columns=['vollcode', 'oppervlakte_land_m2'])
        # temp = self.data.merge(m2)

        # Normalize by dividing by total city
        total_m2_stad = sum(vollcodes_m2_land.values())
        # self.data[col] = (temp.data[col] / total_m2_stad) * temp.data.oppervlakte_land_m2
        self.data[col] = self.data[col] / total_m2_stad

        # Remove m2 colums
        # temp.drop('oppervlakte_land_m2', axis=1, inplace=True)


    def aggregate_on_column(self, col):
        """Aggregate the dataframe in self.data on the given column."""

        # TODO: (4) Implement aggregate on column method.
        pass


    def create_pattern(self, time_period, area_precision):
        """Create a crowdedness pattern.

        The crowdedness pattern is computed for the given time period and area precision (grainedness).

        Keyword arguments:
        time_period - the period for which we create the pattern (e.g. 'day', 'week', 'year')
        area_precision - the "area" precision of the pattern (e.g. 'lat/long', 'vollcode', 'stadsdeelcode', 'stad')
        """

        # TODO: Implement pattern creation method
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
        self.import_data(['gvb'],
                         ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])
        self.dataset_specific()
        self.rename({'incoming': 'gvb_stad'})
        # self.normalize_acreage_city('gvb_stad')


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
        self.import_data(['gvb'],
                         ['halte', 'incoming', 'timestamp', 'lat', 'lon', 'vollcode'])
        self.dataset_specific()
        self.rename({'incoming': 'gvb_buurt'})
        # self.normalize_acreage('gvb_buurt')


    def dataset_specific(self):
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = self.data.halte.isin(haltes)

        # Buurtniveau
        gvb_buurt = self.data.loc[np.logical_not(indx), :]
        self.data = gvb_buurt.groupby(['vollcode', 'weekday', 'hour'])['incoming'].mean().reset_index()

##############################################################################
class Process_alpha_locations_expected(Process):
    """
    This class implements all data importing and pre-processing steps for the
    Alpha datasource. This class only looks at the Alpha data dump file in the
    objectstore (which is imported on a daily basis from Quantillion).
    """

    def __init__(self, dbconfig, aggregation_level):
        super().__init__(dbconfig)
        self.name = 'alpha_locations_expected'
        self.import_data(['alpha_locations_expected'],
                         ['name', 'weekday', 'hour', 'expected', 'vollcode', 'hotspot', 'stadsdeelcode',
                          'main_category', 'main_category_weight'])
        self.dataset_specific(aggregation_level)
        self.rename({'expected': 'alpha'})


    # TODO: Create fallbacks based on an aggregation-level list (now we default to stadsdeel level)
    # TODO: e.g. levels = ['hotspot', 'vollcode', 'stadsdeelcode', 'stad']
    def dataset_specific(self, aggregation_level):
        area_mapping = self.data[[aggregation_level, 'stadsdeelcode']].drop_duplicates()

        # Weight Alpha locations based on the main location category weight.
        self.data['expected'] *= self.data['main_category_weight']

        # historical weekpatroon
        # first calculate the average weekpatroon per location
        google_week_location = self.data.groupby([
            'weekday', 'hour', aggregation_level, 'name'])['expected'].mean().reset_index()
        google_week_location = google_week_location.merge(area_mapping, on=aggregation_level)

        # and then calculate the average weekpatroon per hotspot/vollcode/other aggregation level
        google_week = google_week_location.groupby([
            aggregation_level, 'weekday', 'hour'])['expected'].mean().reset_index()

        # also calculate the average weekpatroon per stadsdeel
        google_week_stadsdeel = google_week_location.groupby([
            'stadsdeelcode', 'weekday', 'hour'])['expected'].mean().reset_index()

        # # Merge the main_category and main_category_weights columns back into the dataframes
        # google_week = google_week.merge(self.data.loc[:, [aggregation_level, 'weekday', 'hour', 'main_category',
        #                                                'main_category_weight']], how='left',
        #                                                 on=[aggregation_level, 'weekday', 'hour'])
        # google_week_stadsdeel = google_week_stadsdeel.merge(self.data.loc[:, ['stadsdeelcode', 'weekday', 'hour',
        #                                                 'main_category', 'main_category_weight']], how='left',
        #                                                 on=['stadsdeelcode', 'weekday', 'hour'])

        # set arbitrary threshold on how many out of 168 hours in a week need to contain measurements, per vollcode.
        # in case of sparse data, take the stadsdeelcode aggregation
        minimal_hours = 98
        cnt = google_week[aggregation_level].value_counts()
        sparse_agglevels = cnt[cnt < minimal_hours].index.tolist()

        # first take the vollcode aggregation for vollcodes that have enough data
        google_week = google_week[~google_week.vollcode.isin(sparse_agglevels)]

        # then take the staddeelcode aggregation for vollcodes for which data is sparse
        google_week_stadsdeel = google_week_stadsdeel.merge(area_mapping, on='stadsdeelcode')
        google_week_stadsdeel.drop('stadsdeelcode', axis=1, inplace=True)
        google_week_stadsdeel = google_week_stadsdeel[google_week_stadsdeel.vollcode.isin(sparse_agglevels)]

        self.data = pd.concat([google_week, google_week_stadsdeel])

##############################################################################
class Process_verblijversindex(Process):
    """This class implements all data importing and pre-processing steps for the verblijversindex datasource."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'verblijversindex'
        self.import_data(['verblijversindex'],
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
        # self.normalize('tellus')

##############################################################################
class Process_buurtcombinatie(Process):
    """This class implements all data importing and pre-processing steps for the buurtcombinatie codes dataset."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'bc_codes'
        self.import_data(['buurtcombinatie'], ['vollcode'])


##############################################################################
class Process_drukte(Process):
    """This class implements the drukte process to combine multiple datasources for further analysis."""

    def __init__(self, dbconfig):
        super().__init__(dbconfig)
        self.name = 'drukte'

        # Run import processes of other datasets
        brt = Process_buurtcombinatie(dbconfig)
        vbi = Process_verblijversindex(dbconfig)
        gvb_st = Process_gvb_stad(dbconfig)
        gvb_bc = Process_gvb_buurt(dbconfig)
        # alp_hist = Process_alpha_historical(dbconfig)
        # alp_live = Process_alpha_live(dbconfig)
        alp_vollcode = Process_alpha_locations_expected(dbconfig, 'vollcode')
        # alp_hotspots = Process_alpha_locations_expected(dbconfig, 'hotspot')

        # initialize drukte dataframe
        start = datetime.datetime(2018, 2, 12, 0, 0)  # Start of a week: Monday at midnight
        end = datetime.datetime(2018, 2, 18, 23, 0)  # End of this week: Sunday 1 hour before midnight
        self.data = self.init_drukte_df(start, end, list(vollcodes_m2_land.keys()))

        # merge datasets
        # cols = ['vollcode', 'weekday', 'hour', 'alpha_week', 'hotspot']
        # self.data = pd.merge(
        #     self.data, alp_hist.data[cols],
        #     on=['weekday', 'hour', 'vollcode'], how='left')

        # cols = ['vollcode', 'weekday', 'hour', 'alpha']
        self.data = pd.merge(
            self.data, alp_vollcode.data,
            on=['weekday', 'hour', 'vollcode'], how='left')

        self.data = pd.merge(
            self.data, gvb_bc.data,
            on=['vollcode', 'weekday', 'hour'], how='left')

        self.data = pd.merge(
            self.data, gvb_st.data,
            on=['weekday', 'hour'], how='left')

        self.data = pd.merge(
            self.data, vbi.data,
            on='vollcode', how='left')

        # Init drukte index
        self.data['drukteindex'] = 0

        # Init hotspot dataframe
        # self.hotspots = alp_hotspots

        # Remove timestamps from weekpattern (only day and hour are relevant)
        self.data.drop('timestamp', axis=1, inplace=True)


    def init_drukte_df(self, start_datetime, end_datetime, vollcodes):
        """This function creates a dataframe with weekdays, hours and vollcodes for a given time period."""
        timestamps = pd.date_range(start=start_datetime, end=end_datetime, freq='H')
        ts_vc = [(ts, vc) for ts in timestamps for vc in vollcodes]
        df = pd.DataFrame({
            'timestamp': [x[0] for x in ts_vc],
            'vollcode': [x[1] for x in ts_vc]
        }).sort_values(['timestamp', 'vollcode'])
        df['weekday'] = [ts.weekday() for ts in df.timestamp]
        df['hour'] = [ts.hour for ts in df.timestamp]
        return df