"""Import data and calculate drukte index."""

import configparser
import argparse
import logging
import pandas as pd
import numpy as np

from scipy.stats import rankdata
from functools import reduce
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from datetime import timedelta

from sklearn.preprocessing import MinMaxScaler

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
    x = (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
    return x


# def normalize(x):
#     """Normalize a numeric array."""
#     x = np.array(x)
#     indx = np.logical_not(np.isnan(x))
#     x_rank = rankdata(x[indx])
#     x[indx] = x_rank
#     return min_max(x)


# def normalize(x, min_x=3, max_x=3):
#     """Normalize a numeric array."""
#     x = np.array(x)
#     x = (x - np.nanmean(x)) / np.nanstd(x)
#     x[x < min_x] = min_x
#     x[x > max_x] = max_x
#     return min_max(x)


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
    verblijversindex = verblijversindex[['wijk', 'verblijversindex']]
    verblijversindex.rename(columns={'wijk': 'vollcode'}, inplace=True)
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

    # add time data
    google['weekday'] = [ts.weekday() for ts in google.timestamp]
    google['hour'] = [ts.hour for ts in google.timestamp]
    google_week = google.loc[google.historical.notnull(), :]

    # historical weekpatroon
    google_week = google_week.groupby([
        'weekday', 'hour', 'vollcode', 'place_id'])['historical'].mean()
    google_week = google_week.reset_index()
    google_week = google_week.groupby([
        'vollcode', 'weekday', 'hour'])['historical'].mean()
    google_week = google_week.reset_index()

    # live data
    google_live = google[['place_id', 'vollcode', 'timestamp', 'live']]
    google_live = google_live.loc[google_live.live.notnull(), :]

    google_live = google_live.groupby(['vollcode', 'timestamp'])['live'].mean()
    google_live = google_live.reset_index()
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
    gvb_stad = gvb_stad.groupby(['weekday', 'hour'])['incoming'].mean()
    gvb_stad = gvb_stad.reset_index()

    # per buurt
    gvb_buurt = gvb.loc[np.logical_not(indx), :]
    gvb_buurt = gvb_buurt.groupby([
        'vollcode', 'weekday', 'hour'])['incoming'].mean().reset_index()

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


def main():
    """Run program."""

    # create connection
    conn = get_conn(dbconfig=args.dbConfig[0])

    # base call
    sql_query = """ SELECT * FROM "{}" """

    # import required sources
    buurtcodes = pd.read_sql(sql=sql_query.format('buurtcombinatie'), con=conn)
    verblijversindex = import_verblijversindex(sql_query=sql_query, conn=conn)
    google_week, google_live = import_google(sql_query, conn)

    haltes = list(pd.read_csv('metro_or_train.csv', sep=',')['station'])
    gvb_stad, gvb_buurt = import_gvb(sql_query, conn, haltes)

        # vollcodes_centrum = [bc for bc in buurtcodes.vollcode.unique()
    #                      if 'A' in bc]
    # tellus = import_tellus(sql_query, conn, vollcodes_centrum)

    # initialize drukte dataframe
    start = np.min(google_live.timestamp)
    end = np.max(google_live.timestamp)
    vollcodes = list(buurtcodes.vollcode.unique())
    drukte = init_drukte_df(start, end, vollcodes)

    # merge datasets
    cols = ['timestamp', 'vollcode', 'google_live']
    drukte = pd.merge(
        drukte, google_live[cols], on=['timestamp', 'vollcode'], how='left')

    cols = ['vollcode', 'weekday', 'hour', 'google_week']
    drukte = pd.merge(
        drukte, google_week[cols],
        on=['weekday', 'hour', 'vollcode'], how='left')

    drukte = pd.merge(
        drukte, gvb_buurt,
        on=['vollcode', 'weekday', 'hour'], how='left')

    drukte = pd.merge(
        drukte, gvb_stad,
        on=['weekday', 'hour'], how='left')

    drukte = pd.merge(
        drukte, verblijversindex,
        on='vollcode', how='left')

    # rank and scale
    float_cols = drukte.select_dtypes(include=['float64']).columns.tolist()
    drukte[float_cols] = drukte[float_cols].rank(axis=1)
    drukte[float_cols] = drukte[float_cols].apply(lambda x: min_max(x), axis=1)

    # schaal verblijversindex naar [1, 3]
    drukte['verblijversindex'] = min_max(drukte['verblijversindex'])
    drukte['verblijversindex'] = (drukte['verblijversindex'] * 2) + 1

    # middel google
    drukte['google'] = drukte[['google_week', 'google_live']].mean(axis=1)

    # middel gvb
    drukte['gvb'] = drukte[['gvb_buurt', 'gvb_stad']].mean(axis=1)

    # schaal kolommen waar nodig
    drukte['google'] = min_max(drukte.google)
    drukte['gvb'] = min_max(drukte.gvb)

    # init drukte index
    drukte['drukte_index'] = np.nan

    linear_weigths = {'verblijversindex': 0,
                      'google': 0,
                      'gvb': 1,
                      'google_week': 0,
                      'google_live': 0}

    for col, weight in linear_weigths.items():
        if col in drukte.columns:
            drukte['drukte_index'] = drukte['drukte_index'].add(drukte[col]*weight, fill_value=0)


    #drukte['drukte_index'] = drukte.drukte_index * drukte.verblijversindex
    #indx = drukte.drukte_index.isnull()
    #drukte.loc[indx, 'drukte_index'] = 0

    #drukte['drukte_index'] = min_max(drukte['drukte_index'])

    # sort values
    drukte = drukte.sort_values(['timestamp', 'vollcode'])

    log.debug('writing data to db')
    drukte.to_sql(
        name='drukteindex', con=conn, index=True, if_exists='replace')
    conn.execute('ALTER TABLE "drukteindex" ADD PRIMARY KEY ("index")')
    log.debug('done.')

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
