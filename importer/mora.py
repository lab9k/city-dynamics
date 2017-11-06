import os
import re
import csv

import pandas as pd
import numpy as np
from datetime import datetime, date, time

def to_database(tablename, conn, datadir, filename='MORA_data_data.csv'):
    # read mora csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter=';')

    # select Hoofdrubriek, Subrubriek, Lattitude, Longitude
    df_select = df.loc[:,['Hoofdrubriek', 'Subrubriek', 'Lattitude', 'Longitude']]

    # rename columns
    df_select.rename(columns={'Hoofdrubriek':'hoofdrubriek', 'Subrubriek':'subrubriek', 'Lattitude':'lat', 'Longitude':'lng'}, inplace=True)

    # add date time column als datetime object
    df_select['timestamp'] = pd.to_datetime(df['AA_ADWH_DATUM_AFGEROND'], format="%d-%m-%Y %H:%M:%S")
    df_select.to_sql(name=tablename, con=conn, index=False, if_exists='replace')