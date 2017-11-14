import os
import re
import csv
import pandas as pd
import numpy as np

def to_database(tablename, conn, datadir, filename='tellus_1M.csv'):
    # read mora csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter='\t', encoding='utf-16')

    # select Latitude, Longitude, Meetwaarde, Representatief, Richting, Richting 1, Richting 2
    # representatief is of het een feestdag (1) is of een representatieve dag (3)
    df_select = df.loc[:,['Latitude', 'Longitude', 'Meetwaarde', 'Representatief', 'Richting', 'Richting 1', 'Richting 2']]

    # Vaak wordt als tijd 00:00:00 gegeven, de date time parser laat dit weg. Dus als er geen tijd is, was het in het oorspronkelijk bestand 00:00:00. 
    df_select['timestamp from'] = pd.to_datetime(df['Tijd Van'], format="%d/%m/%Y %H:%M:%S")
    df_select['timestamp to'] = pd.to_datetime(df['Tijd Tot'], format="%d/%m/%Y %H:%M:%S")

    # rename columns
    df_select.rename(columns={'Latitude':'lat', 'Longitude':'lon', 'Meetwaarde':'meetwaarde', 'Representatief':'representatief', 'Richting':'richting', 'Richting 1':'richting 1', 'Richting 2':'richting 2'}, inplace=True)

    # change comma to dot and type object to type float64
    df_select['lon'] = df_select['lon'].str.replace(',','.')
    df_select['lat'] = df_select['lat'].str.replace(',','.')

    df_select['lon'] = pd.to_numeric(df_select['lon'], errors='coerce')
    df_select['lat'] = pd.to_numeric(df_select['lat'], errors='coerce')

    # filter NaN
    indx = np.logical_or(np.isnan(df_select.lat), np.isnan(df_select.lon))
    indx = np.logical_not(indx)
    df_select = df_select.loc[indx, :]

    df_select.to_sql(name=tablename, con=conn, index=False, if_exists='replace')