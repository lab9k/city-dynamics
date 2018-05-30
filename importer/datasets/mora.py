"""
Load mora data.
"""
import os
import pandas as pd
import numpy as np


def parse(datadir, filename='MORA_data_data.csv'):
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
