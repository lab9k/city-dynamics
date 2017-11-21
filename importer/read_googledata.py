import os
import datetime
import numpy as np
import pandas as pd

# get list of all files
datadir = '/home/rluijk/Documents/GemeenteAmsterdam/google_livescraper'
filenames = os.listdir(datadir)

# remove zip, leave only csv
filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(datadir)) for f in fn]
filenames = [fn for fn in filenames if os.path.splitext(fn)[1] == '.csv']

# columns to select
cols = ['Location', 'Expected', 'Observed', 'ScrapeTime']

def get_timestamp(ts):
    """
    Function to convert month to a numeric value
    """
    conversion = {
        'Jan': '1',
        'Feb': '2',
        'Mar': '3',
        'Apr': '4',
        'May': '5',
        'Jun': '6',
        'Jul': '7',
        'Aug': '8',
        'Sep': '9',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    ts = ts.split(' ')
    month = conversion[ts[1]]
    day = ts[2]
    year = ts[4]
    time = ts[3]
    return '{}-{}-{} {}'.format(year, month, day, time)

def get_strptime(ts):
    """
    Converts string to datetime format
    """
    try:
        return datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
    except:
        None

def read_file(fname, cols=cols):
    """
    Read google data, adding a timestamp
    which is a datetime object
    """
    try:
        df = pd.read_csv(fname, sep=';').loc[:, cols]
        df['timestamp'] = [get_strptime(get_timestamp(ts)) for ts in df.ScrapeTime]
        df.drop('ScrapeTime', axis=1, inplace=True)
        indx = np.logical_not(df.timestamp.isnull())
        df = df.loc[indx, :]
        return df
    except:
        return None

# read data files and concatenate
data = [read_file(fn) for fn in filenames]
data = pd.concat(data)

# # read details of locations
# locations = pd.read_csv('/home/rluijk/Documents/GemeenteAmsterdam/ScrapeList2k/locations2k_details.csv', sep=';')
locations['Location'] = [row['name'] + ', ' + row['address'] for _, row in locations.iterrows()]
locations.drop('id', axis=1, inplace=True)

# # add geometry, types
# data = pd.merge(data, locations, on='Location')

# write to csv
fname = os.path.join(datadir, 'google_oct_nov2017.csv')
data.to_csv(fname, index=False, sep=';')