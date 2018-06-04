"""
This module contains a parser to pre-process data
some small datasource. BIG ones get their own code
in datasets
"""

import os
import datetime
import numpy as np
import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)


def parse_gebieden(datadir, filename='GEBIED_BUURTCOMBINATIES.csv'):
    """Parser for geomapping data."""

    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, sep=';')
    df.drop('Unnamed: 8', axis=1, inplace=True)

    return df


def parse_hotspots(datadir, filename='hotspots_dev.csv'):
    """Parser for hotspots definition file."""
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path)

    return df


def parse_functiekaart(datadir, filename='FUNCTIEKAART.csv'):
    """Parser for funciekaart data."""

    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, sep=';')
    return df


def parse_cmsa(datadir):
    """Parser for CMSA data."""

    def read_file(file, datadir):
        cam_number = re.sub('_.*', '', file.replace('Cam_loc', ''))
        df = pd.read_csv(os.path.join(datadir, file), sep=',')
        df.drop('Unnamed: 3', axis=1, inplace=True)
        df['cam_number'] = cam_number
        return df

    paths = os.listdir(datadir)
    cam_paths = [p for p in paths if 'Cam_loc' in p]
    data = [read_file(file=file, datadir=datadir) for file in cam_paths]
    data = pd.concat(data, ignore_index=True)
    data.rename(columns={'Time': 'timestamp',
                         'In': 'in', 'Out': 'out'}, inplace=True)
    data['timestamp'] = [ts + ':00' for ts in data.timestamp]
    data['timestamp'] = [datetime.datetime.strptime(
        ts, '%Y-%m-%d %H:%M:%S') for ts in data.timestamp]
    return data


def parse_afval(datadir, filename='WEEGGEGEVENS(1-10_30-11_2017).csv'):
    """Parser for AFVAL data."""

    fname = os.path.join(datadir, filename)
    df = pd.read_csv(fname, sep=';')
    df = df.loc[:, ['datum', 'tijd', 'fractie',
                    'nettogewicht', 'breedtegraad', 'lengtegraad']]
    df['DateTime'] = df[['datum', 'tijd']].apply(lambda x: ''.join(x), axis=1)
    df['timestamp'] = pd.to_datetime(df['DateTime'], format="%d/%m/%Y%H:%M:%S")
    df = df.drop(['datum', 'tijd', 'DateTime'], axis=1)
    df.rename(columns={'breedtegraad': 'lat',
                       'lengtegraad': 'lon'}, inplace=True)

    # change comma to dot and type object to type float64
    df['lon'] = df['lon'].str.replace(',', '.')
    df['lat'] = df['lat'].str.replace(',', '.')

    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')

    # filter NaN
    indx = np.logical_or(np.isnan(df.lat), np.isnan(df.lon))
    indx = np.logical_not(indx)
    df = df.loc[indx, :]

    return df


def parse_parkeren(datadir):
    """Parser for PARKEER data."""

    files = os.listdir(datadir)

    # do this with the right regex..
    filenames = []

    for filename in files:
        if '2018_w16' in filename:
            if 'BETAALDP.csv' in filename:
                if 'Ma_Fr' not in filename:
                    if 'Sa_Su' not in filename:
                        filenames.append(filename)
    # BORKED.
    # return df_parkeer
