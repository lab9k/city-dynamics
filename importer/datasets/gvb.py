"""
Load gvb data. Refactor this shit.
"""
import datetime
import os
import pandas as pd

xlsx_file = 'Ortnr - coordinaten (ingangsdatum dec 2015) met LAT LONG.xlsx'


def parse(
        datadir, rittenpath='Ritten GVB 24jun2017-7okt2017.csv',
        locationspath=xlsx_file):
    """Parser for GVB data."""

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
    ritten.columns = ['weekdag', 'tijdstip', 'ortnr_start',
                      'haltenaam_start', 'ortnr_eind', 'tot_ritten']
    ritten.drop('haltenaam_start', axis=1, inplace=True)

    # read locations
    locationspath = os.path.join(datadir, locationspath)
    locations = pd.read_excel(locationspath)
    locations.drop(['X_COORDINAAT', 'Y_COORDINAAT'], axis=1, inplace=True)

    # drop unknown haltes
    locations = locations.loc[locations.haltenaam != '-- Leeg beeld --']

    # add start to ritten
    newnames = dict(OrtNr='ortnr_start', haltenaam='haltenaam_start',
                    LAT='lat_start', LONG='lng_start')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_start')

    # add end to ritten
    newnames = dict(ortnr_start='ortnr_eind', haltenaam_start='haltenaam_eind',
                    lat_start='lat_eind', lng_start='lng_eind')
    locations.rename(columns=newnames, inplace=True)
    ritten = pd.merge(ritten, locations, on='ortnr_eind')

    # incoming ritten
    incoming = ritten.groupby(['haltenaam_eind', 'weekdag', 'tijdstip'])[
        'tot_ritten'].sum().reset_index()
    incoming.rename(columns={'haltenaam_eind': 'halte',
                             'tot_ritten': 'incoming'}, inplace=True)

    # outgoing ritten
    outgoing = ritten.groupby(['haltenaam_start', 'weekdag', 'tijdstip'])[
        'tot_ritten'].sum().reset_index()
    outgoing.rename(columns={'haltenaam_start': 'halte',
                             'tot_ritten': 'outgoing'}, inplace=True)

    # merge incoming, outgoing
    inout = pd.merge(incoming, outgoing, on=['halte', 'weekdag', 'tijdstip'])

    # del incoming, outgoing, data
    del incoming, outgoing, ritten

    # fix tijdstip to hour
    inout['tijd'] = [t.split(':')[0] + ':00' for t in inout.tijdstip]

    # aggregate to hour
    inout = inout.groupby(['halte', 'weekdag', 'tijd'])[
        'incoming', 'outgoing'].sum().reset_index()

    # dag van de week to numeric
    days = dict(ma=1, di=2, wo=3, do=4, vr=5, za=6, zo=7)
    inout['day_numeric'] = [days[d] for d in inout.weekdag]

    # time range
    inout['tijd_numeric'] = [int(t.split(':')[0]) for t in inout.tijd]

    # fix hour over 24
    inout.drop('weekdag', axis=1, inplace=True)
    fixed_time_day = [fix_times(t, d) for t, d in zip(
        inout.tijd_numeric, inout.day_numeric)]
    inout['tijd_numeric'] = [x[0] for x in fixed_time_day]
    inout['day_numeric'] = [x[1] for x in fixed_time_day]

    # add timestamp, fake date, mon 16 oct - sun 22 oct
    dates = ['2017-12-' + str(i) for i in range(4, 11)]
    inout['date'] = [dates[d - 1] for d in inout.day_numeric]
    inout['timestamp'] = [get_datetime(row) for _, row in inout.iterrows()]

    # mean locaties
    locations.rename(columns={
        'ortnr_eind': 'ortnr',
        'haltenaam_eind': 'halte',
        'lat_eind': 'lat',
        'lng_eind': 'lon'}, inplace=True)
    mean_locations = locations.groupby(
        'halte')['lat', 'lon'].mean().reset_index()
    mean_locations = mean_locations[mean_locations.halte != '-- Leeg beeld --']

    # add lat/long coordinates
    inout = pd.merge(inout, mean_locations, on='halte')

    # drop obsolete columns
    inout.drop(['tijd_numeric', 'tijd', 'date'], axis=1, inplace=True)

    return inout
