import os
import argparse
import configparser
import datetime
import numpy as np
import pandas as pd
import re
import csv


def parse_gvb(datadir, rittenpath='Ritten GVB 24jun2017-7okt2017.csv', locationspath='Ortnr - coordinaten (ingangsdatum dec 2015) met LAT LONG.xlsx'):
    
    def fix_times(t, d):
        if t >= 24:
            t -= 24
            if d == 1:
                d = 7
            else:
                d -= 1  
        return t, d

    def get_datetime(row):
        t = datetime.time(row.tijd_numeric, 0)
        d = [int(e) for e in row.date.split('-')]
        d = datetime.date(d[0], d[1], d[2])
        dt = datetime.datetime.combine(d, t)
        return dt


    # read raw ritten
    rittenpath = os.path.join(datadir, rittenpath)
    ritten = pd.read_csv(rittenpath, skiprows=2, header=None)
    ritten.columns = ['weekdag', 'tijdstip', 'ortnr_start', 'haltenaam_start', 'ortnr_eind', 'tot_ritten']
    ritten.drop('haltenaam_start', axis=1, inplace=True)
    
    # read locations
    locationspath = os.path.join(datadir, locationspath)
    locations = pd.read_excel(locationspath)
    locations.drop(['X_COORDINAAT', 'Y_COORDINAAT'], axis=1, inplace=True)
    
    # drop unknown haltes
    locations = locations.loc[locations.haltenaam != '-- Leeg beeld --']
    
    # add start to ritten
    newnames = dict(OrtNr='ortnr_start', haltenaam='haltenaam_start', LAT='lat_start', LONG='lng_start')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_start')
    
    # add end to ritten
    newnames = dict(ortnr_start='ortnr_eind', haltenaam_start='haltenaam_eind', lat_start='lat_eind', lng_start='lng_eind')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_eind')
    
    # incoming ritten
    incoming = ritten.groupby(['haltenaam_eind', 'weekdag', 'tijdstip'])['tot_ritten'].sum().reset_index()
    incoming.rename(columns={'haltenaam_eind':'halte', 'tot_ritten':'incoming'}, inplace=True)
    
    # outgoing ritten
    outgoing = ritten.groupby(['haltenaam_start', 'weekdag', 'tijdstip'])['tot_ritten'].sum().reset_index()
    outgoing.rename(columns={'haltenaam_start': 'halte', 'tot_ritten':'outgoing'}, inplace=True)
    
    # merge incoming, outgoing
    inout = pd.merge(incoming, outgoing, on=['halte', 'weekdag', 'tijdstip'])
    
    # del incoming, outgoing, data
    del incoming, outgoing, ritten
    
    # fix tijdstip to hour
    inout['tijd'] = [t.split(':')[0] + ':00' for t in inout.tijdstip]
    
    # aggregate to hour
    inout = inout.groupby(['halte', 'weekdag', 'tijd'])['incoming', 'outgoing'].sum().reset_index()
    
    # dag van de week to numeric
    days = dict(ma=1, di=2, wo=3, do=4, vr=5, za=6, zo=7)
    inout['day_numeric'] = [days[d] for d in inout.weekdag]
        
    # time range
    inout['tijd_numeric'] = [int(t.split(':')[0]) for t in inout.tijd]

    # fix hour over 24
    inout.drop('weekdag', axis=1, inplace=True)
    fixed_time_day = [fix_times(t, d) for t, d in zip(inout.tijd_numeric, inout.day_numeric)]
    inout['tijd_numeric'] = [x[0] for x in fixed_time_day]
    inout['day_numeric'] = [x[1] for x in fixed_time_day]

    # add timestamp, fake date, mon 16 oct - sun 22 oct
    dates = ['2017-10-' + str(i) for i in range(16, 23)]
    inout['date'] = [dates[d-1] for d in inout.day_numeric]
    inout['timestamp'] = [get_datetime(row) for _, row in inout.iterrows()]
    
    # mean locaties
    locations.rename(columns={'ortnr_eind':'ortnr', 'haltenaam_eind':'halte', 'lat_eind':'lat', 'lng_eind':'lon'}, inplace=True)
    mean_locations = locations.groupby('halte')['lat', 'lon'].mean().reset_index()
    mean_locations = mean_locations[mean_locations.halte != '-- Leeg beeld --']
    
    # add lat/long coordinates
    inout = pd.merge(inout, mean_locations, on='halte')

    # drop obsolete columns
    inout.drop(['tijd_numeric', 'tijd', 'date'], axis=1, inplace=True)
    
    return inout


def parse_google(datadir, filename='google_oct_nov2017.csv', locationsfile='locations2k_details.csv'):
    # read google csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter=';')

    # remove data with no values
    df = df.loc[df.Expected != 'No Expected Value', :]

    # convert to numeric
    df['historical'] = df.Expected.astype(float)
    df['live'] = df.Observed.astype(float)

    df.drop(['Expected', 'Observed'], axis=1, inplace=True)

    # read location file
    path = os.path.join(datadir, locationsfile)
    locations = pd.read_csv(path, sep=';')

    # create Location column
    locations['Location'] = [row['name'] + ', ' + row['address'] for _, row in locations.iterrows()]
    locations.drop('id', axis=1, inplace=True)

    # change longitude column name
    locations.rename(columns={'lng': 'lon'}, inplace=True)

    # drop duplicated locations
    indx = np.logical_not(locations.Location.duplicated())
    locations = locations.loc[indx, :]

    # add geometry, types
    df = pd.merge(df, locations, on='Location')

    # create timestamp
    df['timestamp'] = [datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in df.timestamp]

    # create column: difference between expected, observed
    df['differences'] = df.historical - df.live

    return df


def parse_mora(datadir, filename='MORA_data_data.csv'):
    # read mora csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter=';')

    # select Hoofdrubriek, Subrubriek, Lattitude, Longitude
    df_select = df.loc[:,['Hoofdrubriek', 'Subrubriek', 'Lattitude', 'Longitude']]

    # rename columns
    df_select.rename(columns={'Hoofdrubriek':'hoofdrubriek', 'Subrubriek':'subrubriek', 'Lattitude':'lat', 'Longitude':'lon'}, inplace=True)

    # add date time column als datetime object
    df_select['timestamp'] = pd.to_datetime(df['AA_ADWH_DATUM_AFGEROND'], format="%d-%m-%Y %H:%M:%S")

    # filter NaN
    indx = np.logical_or(np.isnan(df_select.lat), np.isnan(df_select.lon))
    indx = np.logical_not(indx)
    df_select = df_select.loc[indx, :]

    return df_select


def parse_tellus(datadir, filename='tellus2017.csv'):
    # read tellus csv
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, delimiter=';', encoding='utf-8', nrows=1e5)

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

    return df_select

def parse_geomapping(datadir, filename='GEBIED_BUURTCOMBINATIES.csv'):
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, sep=';')
    df.drop('Unnamed: 8', axis=1, inplace=True)

    return df

def parse_functiekaart(datadir, filename='FUNCTIEKAART.csv'):
    path = os.path.join(datadir, filename)
    df = pd.read_csv(path, sep=';')
    return df

def parse_verblijversindex(datadir, filename='Samenvoegingverblijvers2016_Tamas.xlsx'):
    path = os.path.join(datadir, filename)
    df = pd.read_excel(path, sheet_name=3)
    indx = np.logical_and(df.wijk != 'gemiddelde', np.logical_not(df.wijk.isnull()))
    cols = ['wijk', 'oppervlakte land in vierkante meters', 'verbl. Per HA (land) 2016']
    df = df.loc[indx, cols]
    df[cols[2]] = np.round(df[cols[2]]).astype(int)
    df.columns = ['wijk', 'oppervlakte_m2', 'verblijversindex']
    return df