"""
Module should implement class 'Process'.

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

##############################################################################
class Process():
    """This class implements the process of loading and pre-processing all data from one datasource."""

    def __init__(self):
        self.name = ''                  # Name of datasource
        self.data = pd.DataFrame()      # Data of datasource
        self.conn = ''                  # Database connection of datasource

    def __str__(self):
        """Print string representation of Process"""
        return "Dataset name: %s\nData: %s" % (self.name, self.data)


    def connect_database(self, dbconfig):
        """Create a connection with the datasource storage."""
        postgres_url = URL(
            drivername='postgresql',
            host=config_auth.get(dbconfig, 'host'),
            port=config_auth.get(dbconfig, 'port'),
            database=config_auth.get(dbconfig, 'dbname'),
            username=config_auth.get(dbconfig, 'user'),
            password=config_auth.get(dbconfig, 'password')
        )
        self.conn = create_engine(postgres_url)


    def import_data(self, tables, columns):
        """Import the datasource's data from the storage database as a Pandas dataframe."""
        d = dict.fromkeys(tables)
        for table in tables:
            d[table] = self.import_table(table)             # Import each table as dataframe
            if columns == []:
                pass
            else:
                d[table] = d[table][columns]                    # Only select relevant columns
        self.data = pd.concat([v for v in d.values()])      # Combine dataframes
        del d


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
        """Normalize all specified columns. Adapted from: https://stackoverflow.com/a/36475297"""
        if cols_norm != []:
            scaler = preprocessing.MinMaxScaler()
            for col in cols_norm:
                self.data[col + '_normalized'] = scaler.fit_transform(self.data[[col]])


    def normalize_acreage(self, cols_norm_m2):
        """Normalize all specified columns based on the surface area."""
        # TODO: Dit implementeren
        pass


    def run(self, dbconfig, tables, columns, cols_rename, cols_norm_m2, cols_norm):
        """Run the entire data import process."""
        self.connect_database(dbconfig)
        self.import_data(tables, columns)       # Import specified tables/columns. When no columns specified, import all.
        self.process_timestamps()               # If timestamp column exists, create weekday & hour columns
        self.dataset_specific()                 # Run dataset specific data manipulations
        self.rename(cols_rename)                # Rename columns
        self.normalize_acreage(cols_norm_m2)    # Normalize on size of the area
        self.normalize(cols_norm)               # Normalize data in given columns

##############################################################################
class Process_gvb_stad(Process):
    """This class implements all data importing and pre-processing steps, specifically for the GVB datasource."""

    def __init__(self, dbconfig):
        super().__init__()
        self.name = 'gvb_stad'                          # Name of the datasource
        tables = ['gvb_with_bc']                        # Tables to be imported
        columns = ['halte', 'incoming', 'timestamp',    # Columns to be selected
                   'lat', 'lon', 'vollcode']
        cols_rename = {'incoming': 'gvb_stad'}          # Columns to be renamed, e.g.  [(old, new)]
        cols_norm_m2 = []                               # Columns to be normalized based on surface area
        cols_norm = []                                  # Columns to be normalized
        self.run(dbconfig, tables, columns,             # Run import process
                 cols_rename, cols_norm_m2, cols_norm)

    def dataset_specific(self):
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = self.data.halte.isin(haltes)

        # Stadsniveau
        gvb_stad = self.data.loc[indx, :]
        gvb_stad = gvb_stad.groupby(['weekday', 'hour'])['incoming'].mean()
        self.data = gvb_stad.reset_index()

##############################################################################
class Process_gvb_buurt(Process):
    """This class implements all data importing and pre-processing steps, specifically for the GVB datasource."""

    def __init__(self, dbconfig):
        super().__init__()
        self.name = 'gvb_buurt'                         # Name of the datasource
        tables = ['gvb_with_bc']                        # Tables to be imported
        columns = ['halte', 'incoming', 'timestamp',    # Columns to be selected
                   'lat', 'lon', 'vollcode']
        cols_rename = {'incoming': 'gvb_buurt'}         # Columns to be renamed, e.g.  [(old, new)]
        cols_norm = []                                  # Columns to be normalized
        cols_norm_m2 = []                               # Columns to be normalized based on surface area
        self.run(dbconfig, tables, columns,             # Run import process
                 cols_rename, cols_norm_m2, cols_norm)

    def dataset_specific(self):
        haltes = list(pd.read_csv('lookup_tables/metro_or_train.csv', sep=',')['station'])
        indx = self.data.halte.isin(haltes)

        # Buurtniveau
        gvb_buurt = self.data.loc[np.logical_not(indx), :]
        self.data = gvb_buurt.groupby([
            'vollcode', 'weekday', 'hour'])['incoming'].mean().reset_index()

##############################################################################
class Process_alpha(Process):
    """This class implements all data importing and pre-processing steps, specifically for the alpha datasource."""

    def __init__(self, dbconfig):
        Process.__init__(self, 'live', dbconfig)

##############################################################################
class Process_verblijversindex(Process):
    """This class implements all data importing and pre-processing steps for the verblijversindex datasource."""

    def __init__(self, dbconfig):
        super().__init__()
        self.name = 'verblijversindex'                              # Name of the datasource
        tables = ['VERBLIJVERSINDEX']                               # Tables to be imported
        columns = ['wijk', 'verblijversindex', 'oppervlakte_m2']    # Columns to be selected
        cols_rename = {'wijk': 'vollcode'}                          # Columns to be renamed, e.g. {'old': 'new'}
        cols_norm_m2 = []                                           # Columns to be normalized based on surface area
        cols_norm = []                                              # Columns to be normalized
        self.run(dbconfig, tables, columns,                         # Run import process
                 cols_rename, cols_norm_m2, cols_norm)

##############################################################################
class Process_tellus(Process):
    """This class implements all data importing and pre-processing steps for the tellus datasource."""

    def __init__(self, dbconfig):
        super().__init__()
        self.name = 'tellus'                                        # Name of the datasource
        tables = ['tellus_with_bc']                                 # Tables to be imported
        columns = ['meetwaarde', 'timestamp', 'vollcode']           # Columns to be selected
        cols_rename = {'meetwaarde': 'tellus'}                      # Columns to be renamed, e.g. {'old': 'new'}
        cols_norm_m2 = []                                           # Columns to be normalized based on surface area
        cols_norm = []                                              # Columns to be normalized
        self.run(dbconfig, tables, columns,                         # Run import process
                 cols_rename, cols_norm_m2, cols_norm)

    def dataset_specific(self):
        self.data['meetwaarde'] = self.data.meetwaarde.astype(int)
        vollcodes = list(self.data.vollcode.unique())
        vollcodes2 = ['A07', 'F77', 'K53', 'F87', 'K24', 'K44', 'K47', 'M27', 'M28', 'M30', 'N64', 'N66', 'M33', 'N60', 'N61', 'N62', 'N73', 'T93', 'T98', 'K52', 'M29', 'M34', 'A08', 'A09', 'B10', 'F84', 'K59', 'N71', 'N72', 'T95', 'T96', 'E14', 'E17', 'A00', 'A05', 'A03', 'E41', 'E42', 'A04', 'E21', 'E43', 'F76', 'F78', 'F79', 'F81', 'F82', 'F83', 'E20', 'F86', 'E18', 'E19', 'E22', 'K25', 'K45', 'K46', 'N63', 'K49', 'K54', 'T92', 'M31', 'T97', 'M32', 'A01', 'M56', 'M57', 'A02', 'N65', 'F80', 'K48', 'F88', 'E16', 'K23', 'F89', 'A06', 'E40', 'K90', 'E12', 'K91', 'E36', 'E13', 'E15', 'M50', 'E37', 'E38', 'K26', 'E39', 'E75', 'F11', 'N68', 'M35', 'M51', 'M55', 'F85', 'M58', 'N67', 'N69', 'N70', 'N74', 'T94']
        vc_ts = [(vc, ts) for vc in vollcodes2 for ts in self.data.timestamp.unique()]
        vc_ts = pd.DataFrame({
            'vollcode': [x[0] for x in vc_ts],
            'timestamp': [x[1] for x in vc_ts]
        })
        self.data = pd.merge(self.data, vc_ts, on='timestamp', how='outer')

##############################################################################
class Process_buurtcombinatie(Process):

    def __init__(self, dbconfig):
        super().__init__()
        self.name = 'bc_codes'
        tables = ['buurtcombinatie']
        columns = ['vollcode']
        cols_rename = {}
        cols_norm_m2 = []                               # Columns to be normalized based on surface area
        cols_norm = []
        self.run(dbconfig, tables, columns, cols_rename, cols_norm_m2, cols_norm)

##############################################################################
def main():
    """Run the main process of this file: loading all datasets"""

    dbconfig = args.dbConfig[0]  # dbconfig is the same for all datasources now. Could be different in the future.
    # brt = Process_buurtcombinatie(dbconfig)
    # vollcodes = list(brt.data.vollcode.unique())
    # vbi = Process_verblijversindex(dbconfig)
    # gvb_st = Process_gvb_stad(dbconfig)
    # gvb_bc = Process_gvb_buurt(dbconfig)
    tel = Process_tellus(dbconfig)
    q.d()

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
    main()