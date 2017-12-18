import configparser
import argparse
import logging
import pandas as pd
import numpy as np

from scipy.stats import rankdata
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from datetime import date, datetime, timedelta

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


def datetime_range(start, end, delta):
    """Create a range of timestamps."""
    current = start
    if not isinstance(delta, timedelta):
        delta = timedelta(**delta)
    while current < end:
        yield current
        current += delta


def min_max(x):
    """Scale numeric array to [0, 1]."""
    x = np.array(x)
    x = (x - min(x)) / (max(x) - min(x))
    return x


def normalize(x):
    """Normalize a numeric array."""
    x = rankdata(x)
    return min_max(x)


def normalize_data(df, cols):
    """Normalize all specified columns in dataframe."""
    df = df.groupby(['vollcode', 'timestamp'])[cols].mean().reset_index()
    for col in cols:
        new_col = col + '_normalized'
        df[new_col] = df.groupby(['timestamp'])[col].transform(normalize)

    return df


def import_verblijversindex(sql_query, conn):
    """Read data on verblijversindex."""
    verblijversindex = pd.read_sql(
        sql=sql_query.format('VERBLIJVERSINDEX'), con=conn)
    verblijversindex = verblijversindex[['wijk', 'oppervlakte_m2']]
    verblijversindex.rename(columns={
        'wijk': 'vollcode',
        'oppervlakte_m2': 'verblijversindex'
    }, inplace=True)
    verblijversindex = verblijversindex[['vollcode', 'verblijversindex']]
    return verblijversindex


def import_google(sql_query, conn):
    """Function to read google data."""
    def read_table(sql_query, conn):
        df = pd.read_sql(sql=sql_query, con=conn)
        df['timestamp'] = df.timestamp.dt.round('60min')
        df = df[['place_id', 'vollcode', 'timestamp', 'live', 'historical']]
        return df

    # read raw data
    google_octnov = read_table(sql_query.format('google_with_bc'), conn=conn)
    google_dec = read_table(sql_query.format('google_dec_with_bc'), conn=conn)
    google = pd.concat([google_octnov, google_dec])
    del google_octnov, google_dec

    # historical weekpatroon
    google['weekday'] = [ts.weekday() for ts in google.timestamp]
    google['hour'] = [ts.hour for ts in google.timestamp]
    google_week = google.groupby(['weekday', 'hour', 'vollcode', 'place_id'])['historical'].mean().reset_index()
    google_week = google.groupby(['vollcode', 'weekday', 'hour'])['historical'].mean().reset_index()

    # live data
    google_live = google[['place_id', 'vollcode', 'timestamp', 'live']]
    google_live = google_live.groupby(['vollcode', 'timestamp'])['live'].mean().reset_index()
    google_live['weekday'] = [ts.weekday() for ts in google_live.timestamp]
    google_live['hour'] = [ts.hour for ts in google_live.timestamp]

    # column names
    google_live.rename(columns={'live': 'google_live'}, inplace=True)
    google_week.rename(columns={'historical': 'google_week'}, inplace=True)

    return google_week, google_live


def import_gvb(sql_query, conn, haltes):
    """Import GVB data and create weekly pattern."""
    def read_table(sql_query, conn):
        df = pd.read_sql(sql=sql_query, con=conn)
        df['timestamp'] = df.timestamp.dt.round('60min')
        df['weekday'] = [ts.weekday() for ts in df.timestamp]
        df['hour'] = [ts.hour for ts in df.timestamp]
        cols = ['halte', 'incoming', 'weekday',
                'hour', 'lat', 'lon', 'vollcode']
        df = df[cols]
        return df

    # read raw
    gvb = read_table(sql_query.format('gvb_with_bc'), conn=conn)

    # hele stad over tijd
    indx = gvb.halte.isin(haltes)
    gvb_stad = gvb.loc[indx, :]
    gvb_stad = gvb_stad.groupby(['weekday', 'hour'])['incoming'].sum().reset_index()

    # per buurt
    gvb_buurt = gvb.loc[np.logical_not(indx), :]
    gvb_buurt = gvb_buurt.groupby(['vollcode', 'weekday', 'hour'])['incoming'].sum().reset_index()

    # column names
    gvb_stad.rename(columns={'incoming': 'gvb_stad'}, inplace=True)
    gvb_buurt.rename(columns={'incoming': 'gvb_buurt'}, inplace=True)

    return gvb_stad, gvb_buurt


def import_tellus(sql_query, conn, vollcodes):
    """Import and manipulate tellus data."""
    df = pd.read_sql(sql=sql_query.format('tellus_with_bc'), con=conn)
    df['timestamp'] = df.timestamp.dt.round('60min')
    df = df[['meetwaarde', 'timestamp', 'vollcode']]
    df['meetwaarde'] = df.meetwaarde.astype(int)
    df = df.groupby('timestamp')['meetwaarde'].sum().reset_index()

    # add all vollcodes per timestamp
    vc_ts = [(vc, ts) for vc in vollcodes for ts in df.timestamp.unique()]
    vc_ts = pd.DataFrame({
        'vollcode': [x[0] for x in vc_ts],
        'timestamp': [x[1] for x in vc_ts]
    })
    df = pd.merge(df, vc_ts, on='timestamp', how='outer')

    # column names
    df.rename(columns={'meetwaarde': 'tellus'}, inplace=True)

    return df


def dataset_type(cols, to_match=['timestamp', 'vollcode', 'weekday', 'hour']):
    """Determine type of data present in dataframe."""
    cols = np.array(cols)
    if np.all([tm in cols for tm in [to_match[0]]]):
        return 'with_timestamp'
    elif np.all([tm in cols for tm in to_match[1:]]):
        return 'weekday_hour'
    elif 'vollcode' in cols:
        return 'static_vollcode'
    else:
        return 'static_city'


def merge_datasets(**kwargs):
    """Merge datasets.

    Takes named arguments and merges them based on
    the type of data in them.
    """
    dataset_types = {dname: dataset_type(kwargs[dname].columns) for dname in kwargs.keys()}

    drukte_timestamp = [kwargs[dname] for dname in kwargs.keys() if dataset_types[dname] == 'with_timestamp']
    drukte_timestamp = reduce(lambda x, y: pd.merge(x, y, on=['timestamp', 'vollcode'], how='outer'), drukte_timestamp)
    drukte_timestamp['weekday'] = [ts.weekday() for ts in drukte_timestamp.timestamp]
    drukte_timestamp['hour'] = [ts.hour for ts in drukte_timestamp.timestamp]
    drukte_timestamp = drukte_timestamp.drop_duplicates()

    drukte_day_hour = [kwargs[dname] for dname in kwargs.keys() if dataset_types[dname] == 'weekday_hour']
    drukte_day_hour = reduce(lambda x, y: pd.merge(x, y, on=['vollcode', 'weekday', 'hour'], how='outer'), drukte_day_hour)
    drukte_day_hour = drukte_day_hour.drop_duplicates()

    drukte_static_vollcode = [kwargs[dname] for dname in kwargs.keys() if dataset_types[dname] == 'static_vollcode']
    drukte_static_vollcode = reduce(lambda x, y: pd.merge(x, y, on='vollcode', how='outer'), drukte_static_vollcode)
    drukte_static_vollcode = drukte_static_vollcode.drop_duplicates()

    drukte_static_city = [kwargs[dname] for dname in kwargs.keys() if dataset_types[dname] == 'static_city']
    drukte_static_city = reduce(lambda x, y: pd.merge(x, y, on='vollcode', how='outer'), drukte_static_city)
    drukte_static_city = drukte_static_city.drop_duplicates()

    drukte = pd.merge(drukte_timestamp, drukte_day_hour, on=['vollcode', 'weekday', 'hour'], how='outer').drop_duplicates()
    drukte = pd.merge(drukte, drukte_static_vollcode, on='vollcode', how='outer').drop_duplicates()
    drukte = pd.merge(drukte, drukte_static_city, on=['weekday', 'hour'], how='outer').drop_duplicates()

    return drukte


def complete_ts_vollcode(data, vollcodes):
    """Complete dataframe to include all vollcode-timestamp combinations."""
    # get list of timestamps
    start = np.min(data.timestamp)
    end = np.max(data.timestamp)
    timestamps = pd.date_range(start=start, end=end, freq='H')

    # create new dataframe
    ts_vc = [(ts, vc) for ts in timestamps for vc in vollcodes]
    mind = pd.DataFrame({
        'timestamp': [x[0] for x in ts_vc],
        'vollcode': [x[1] for x in ts_vc]
    })

    # merge data
    data = pd.merge(mind, data, on=['timestamp', 'vollcode'], how='left')

    # fill in missing weekdays and hours
    data['weekday'] = [ts.weekday() for ts in data.timestamp]
    data['hour'] = [ts.hour for ts in data.timestamp]

    return data


def weighted_mean(data, cols, weights):
    """Calculate weighted mean."""
    # create numpy array with right columns
    x = np.array(data.loc[:, cols])

    # calculate weight matrix
    n_weights = len(weights)
    weights = np.array(weights * len(x)).reshape(len(x), n_weights)
    weights[np.isnan(x)] = 0

    # calculate overall index
    wmean = np.array(x * weights)
    wmean = np.nansum(wmean, axis=1) / weights.sum(axis=1)

    return wmean


def main():
    """Run program."""
    # create connection
    conn = get_conn(dbconfig=args.dbConfig[0])

    # base call
    sql_query = """ SELECT * FROM "{}" """

    # read buurtcodes
    buurtcodes = pd.read_sql(sql=sql_query.format('buurtcombinatie'), con=conn)

    # verblijversindex
    log.debug('verblijversindex')
    verblijversindex = import_verblijversindex(sql_query=sql_query, conn=conn)

    # read google weekly pattern and live data
    google_week, google_live = import_google(sql_query, conn)

    # read GVB overall city and neighborhood-specific patterns
    haltes = list(pd.read_csv('metro_or_train.csv', sep=',')['station'])
    gvb_stad, gvb_buurt = import_gvb(sql_query, conn, haltes)

    # read tellus for city centre neighborhoods
    vollcodes_centrum = [bc for bc in buurtcodes.vollcode.unique()
                         if 'A' in bc]
    tellus = import_tellus(sql_query, conn, vollcodes_centrum)

    # merge datasets
    log.debug('merge datasets')

    # merge datasetss
    drukte = merge_datasets(
        google_live=google_live,
        google_week=google_week,
        tellus=tellus,
        gvb_stad=gvb_stad,
        gvb_buurt=gvb_buurt,
        verblijversindex=verblijversindex)

    # filter on date
    drukte = drukte.loc[drukte['timestamp'] >= '2017-10-15 00:00:00', :]

    # fill in missing timestamp-vollcode combinations
    all_vollcodes = buurtcodes.vollcode.unique()
    drukte = complete_ts_vollcode(data=drukte, vollcodes=all_vollcodes)

    log.debug('calculating overall index')

    # combine google columns
    google_cols = ['google_live', 'google_week']
    drukte['google'] = drukte[google_cols].mean(axis=1)
    drukte.drop(columns=google_cols, inplace=True)

    # add verblijversindex
    drukte.drop(columns='verblijversindex', inplace=True)
    drukte = pd.merge(drukte, verblijversindex, on='vollcode', how='left')

    # define weights, have to be in same order als columns!
    cols = ['google', 'gvb_buurt', 'verblijversindex']
    drukte = normalize_data(df=drukte, cols=cols)
    weights = [0.6, 0.2, 0.2]
    normalized_cols = [col + '_normalized' for col in cols]
    drukte['drukte_index'] = weighted_mean(
        data=drukte, cols=normalized_cols, weights=weights)

    # drop obsolete columns
    all_cols = cols + normalized_cols
    drukte.drop(columns=all_cols, inplace=True)

    # add buurtcode information
    drukte = pd.merge(drukte, buurtcodes, on='vollcode', how='left')
    log.debug(drukte.columns.tolist())
    # write to db
    log.debug('writing data to db')

    drukte.to_sql(
        name='drukteindex', con=conn, index=True, if_exists='replace')
    conn.execute('ALTER TABLE "drukteindex" ADD PRIMARY KEY ("index")')
    log.debug('Done you are awesome <3')


if __name__ == '__main__':
    desc = "Calculate index."
    log.debug(desc)
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    main()
