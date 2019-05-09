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


def parse_mora(datadir, filename='MORA_data_data.csv'):
    """Parser for MORA data."""

    # read mora csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter=';')

    # select Hoofdrubriek, Subrubriek, Lattitude, Longitude
    df_select = df.loc[
        :, ['Hoofdrubriek', 'Subrubriek', 'Lattitude', 'Longitude']]

    # rename columns
    df_select.rename(columns={
        'Hoofdrubriek': 'hoofdrubriek',
        'Subrubriek': 'subrubriek',
        'Lattitude': 'lat',
        'Longitude': 'lon'}, inplace=True)

    # add date time column als datetime object
    df_select['timestamp'] = pd.to_datetime(
        df['AA_ADWH_DATUM_AFGEROND'], format="%d-%m-%Y %H:%M:%S")

    # filter NaNs
    indx = np.logical_or(np.isnan(df_select.lat), np.isnan(df_select.lon))
    indx = np.logical_not(indx)
    df_select = df_select.loc[indx, :]

    return df_select


def parse_tellus(datadir, filename='tellus2017.csv'):
    """Parser for tellus data."""

    # open tellus csv
    path = os.path.join(datadir, filename)
    file = open(path, 'r', encoding='utf-8')

    # read header
    header = np.array(next(file).strip('\n').split(';'))

    # read data going to centrum
    def read_line(line):
        line = line.strip('\n').split(';')
        if line[5] == 'Centrum' or line[6] == 'Centrum':
            return line

    # read lines
    df = [read_line(line) for line in file]
    df = [line for line in df if line is not None]

    # close file
    file.close()

    # convert to dataframe
    df = pd.DataFrame(df, columns=header)

    # select columns
    df = df.loc[:, ['Tellus Id', 'Latitude', 'Longitude',
                    'Meetwaarde', 'Representatief', 'Richting',
                    'Richting 1', 'Richting 2', 'Tijd Van']]

    # Vaak wordt als tijd 00:00:00 gegeven, de date time parser laat dit weg.
    # Dus als er geen tijd is, was het in het oorspronkelijk bestand 00:00:00.
    df['Tijd Van'] = pd.to_datetime(df['Tijd Van'], format="%d/%m/%Y %H:%M:%S")

    # rename columns
    df.rename(columns={
        'Tellus Id': 'tellus_id', 'Tijd Van': 'timestamp',
        'Latitude': 'lat', 'Longitude': 'lon', 'Meetwaarde': 'tellus',
        'Representatief': 'representatief', 'Richting': 'richting',
        'Richting 1': 'richting_1', 'Richting 2': 'richting_2'}, inplace=True)

    # Process number-strings to int
    df['tellus'] = df.tellus.astype(int)

    # change comma to dot and type object to type float64
    df['lon'] = df['lon'].str.replace(',', '.')
    df['lat'] = df['lat'].str.replace(',', '.')

    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')

    # filter NaN
    indx = np.logical_or(np.isnan(df.lat), np.isnan(df.lon))
    indx = np.logical_not(indx)
    df = df.loc[indx, :]

    # only direction centrum
    indx1 = np.logical_and(df['richting_1'] == 'Centrum', df.richting == '1')
    indx2 = np.logical_and(df['richting_2'] == 'Centrum', df.richting == '2')
    df = df.loc[np.logical_or(indx1, indx2), :]

    # drop columns
    df.drop(['richting', 'richting_1',
             'richting_2', 'representatief'], axis=1, inplace=True)

    return df


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
