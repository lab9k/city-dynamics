"""
Parse Tellus data
"""
import os
import numpy as np
import pandas as pd


def parse(datadir, filename='tellus2017.csv'):
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
