"""
This module contains a parser to pre-process data from every datasource.
"""

import os
import datetime
import numpy as np
import pandas as pd
import re
import glob
from ETLFunctions import DatabaseInteractions
from ETLFunctions import ModifyTables

import logging

logger = logging.getLogger(__name__)


def parse_gvb(datadir,
              rittenpath='Ritten GVB 24jun2017-7okt2017.csv',
              locationspath='Ortnr - coordinaten (ingangsdatum dec 2015) met LAT LONG.xlsx'):
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


def parse_geomapping(datadir, filename='GEBIED_BUURTCOMBINATIES.csv'):
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


def parse_verblijversindex(datadir, filename='Samenvoegingverblijvers2016_Tamas.xlsx'):
    """Parser for verblijversindex data."""

    path = os.path.join(datadir, filename)
    df = pd.read_excel(path, sheet_name=3)

    cols = ['wijk',
            'aantal inwoners',
            'aantal werkzame personen',
            'aantal studenten',
            'aantal  bezoekers (met correctie voor onderlinge overlap)',
            'som alle verblijvers',
            'oppervlakte land in vierkante meters',
            'oppervlakte land en water in vierkante meter',
            'verbl. Per HA (land) 2016']

    df = df[cols]

    # pandas.to_sql can't handle brackets within column names
    df.rename(columns={ 'wijk': 'vollcode',
                        'aantal inwoners': 'inwoners',
                        'aantal werkzame personen': 'werkzame_personen',
                        'aantal studenten': 'studenten',
                        'aantal  bezoekers (met correctie voor onderlinge overlap)': 'bezoekers',
                        'som alle verblijvers': 'verblijvers',
                        'oppervlakte land in vierkante meters': 'oppervlakte_land_m2',
                        'oppervlakte land en water in vierkante meter': 'oppervlakte_land_water_m2',
                        'verbl. Per HA (land) 2016': 'verblijvers_ha_2016'}, inplace=True)

    df = df.head(98)  # Remove last two rows (no relevant data there)
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

    allfiles = glob.glob(datadir + "/2017-10*.csv")
    df_parkeer = pd.DataFrame()
    list_ = []
    for file_ in allfiles:
        df = pd.read_csv(file_, index_col=None, header=0, delimiter=';')
        list_.append(df)
    df_parkeer = pd.concat(list_)
    df_parkeer['DateTime'] = pd.to_datetime(
        df_parkeer['timestamp'], format="%Y-%m-%d %H:%M:%S")
    df_parkeer['weekday'] = df_parkeer.apply(
        lambda x: x['DateTime'].weekday(), axis=1)
    df_parkeer['hour'] = df_parkeer.apply(lambda x: x['DateTime'].hour, axis=1)
    df_parkeer = df_parkeer.replace(0.000000, np.nan)
    df_parkeer = df_parkeer.drop(['timestamp', 'DateTime'], axis=1)

    return df_parkeer


categories_tags_mapping = {'default': ['alles_wat_geen_andere_tag_heeft', 'storage', 'synagogue', 'church', 'place_of_worship',
                            'spa', 'gym'],
                'park': ['park'],
                'ov': ['train_station', 'subway_station', 'bus_station', 'transit_station'],
                'museum': ['museum'],
                'bar': ['bowling_alley', 'casino', 'movie_theatre', 'night_club', 'bar', 'cafe'],
                'restaurant': ['meal_takeaway', 'restaurant'],
                'supermarket': ['markt_winkelcentrum', 'supermarket', 'grocery_or_supermarket'],
                'store': ['beauty_salon', 'laundry', 'bicycle_store', 'hardware_store', 'jewelry_store',
                          'shopping_mall', 'art_gallery', 'liquor_store', 'car_dealer', 'pharmacy', 'department_store',
                          'shoe_store', 'convenience_store', 'furniture_store', 'electronics_store', 'book_store',
                          'gas_station', 'clothing_store', 'bakery', 'home_goods_store', 'store'],
                'service': ['school', 'local_government_office', 'lawyer', 'post_office', 'accounting',
                            'real_estate_agency', 'veteranian_care', 'hospital', 'general_contractor', 'library',
                            'travel_agency', 'meal_delivery', 'car_wash', 'hair_care', 'physiotherapist', 'car_rental',
                            'bank', 'car_repair', 'dentist', 'finance', 'doctor'],
                'disregard': ['point_of_interest', 'establishment', 'food', 'health', 'atm']}

# create the inverse of category_tags_mapping
tags_categories_mapping = {}
for k, v in categories_tags_mapping.items():
    for tag in v:
        tags_categories_mapping[tag] = k


category_weights = {'default': 0.2,
                    'park': 1.0,
                    'ov': 1.0,
                    'museum': 0.3,
                    'bar': 0.35,
                    'restaurant': 0.25,
                    'supermarket': 0.7,
                    'store': 0.4,
                    'service': 0.15,
                    'disregard': 0.0}

categories_list = list(categories_tags_mapping.keys())
tags_list = list(tags_categories_mapping.keys())

def evaluate_tags(tags_to_evaluate):

    # Start with default category.
    # Set weight to -1, since other categories need to be allowed to overwrite the default category.
    main_category = 'default'
    main_category_weight = -1

    # Assign categories to locations based on tags. Only keep the category-tag/weight for the tag with the highest weight.
    for tag in tags_to_evaluate:
        if tag in tags_list:
            cat = tags_categories_mapping[tag]
            if category_weights[cat] > main_category_weight:
                main_category = cat
                main_category_weight = category_weights[cat]

    # If no category was found, set the default category weight.
    if main_category == 'default':
        main_category_weight = category_weights['default']

    return (main_category, main_category_weight)


def parse_alpha_item(conn, i, id_counter, raw):

    # Function to double up quotation marks for sql writing.
    def fix_quotes(x):
        return re.sub("'", "''", x)

    place_id = raw.place_id[i]
    name = raw.name[i]
    url = raw.data[i]['url']
    weekday = raw.scraped_at[i].weekday()
    lat = raw.data[i]['location']['coordinates'][1]
    lon = raw.data[i]['location']['coordinates'][0]
    address = raw.data[i]['formatted_address']
    location_type = raw.data[i]['location']['type']
    main_category, main_category_weight = evaluate_tags(str(raw.data[i]['types']))
    visit_duration = raw.data[i]['VisitDuration']
    types = str(raw.data[i]['types'])
    category = raw.data[i]['Category']

    # Fix quotes for sql writing
    name = fix_quotes(name)
    url = fix_quotes(url)
    address = fix_quotes(address)
    location_type = fix_quotes(location_type)
    visit_duration = fix_quotes(visit_duration)
    types = fix_quotes(types)

    logging.debug(raw.data[i]['Expected'])

    # Loop over all expected hour intervals for each location and scrape day
    for interval in raw.data[i]['Expected']:

        # Truncate time interval to first hour of the interval
        hour = interval['TimeInterval'][0:2]
        hour = int(re.sub("[^0-9]", "", hour))
        ampm = interval['TimeInterval'][1:4]
        ampm = re.sub('[^a-zA-Z]+', '', ampm)
        if ampm == 'pm':
            if hour == 12:
                pass
            else:
                hour += 12

        # Get the expected crowdedness value for this hour (relative value)
        expected = interval['ExpectedValue']

        # Create sql query to write data to database
        row_sql = create_row_sql(id_counter, place_id, name, url, weekday, hour, expected,
                        lat, lon, address, location_type, visit_duration, types, category)

        # Write data to database
        conn.execute(row_sql)

        # Update id counter so all rows have a unique id
        id_counter += 1

    return id_counter


def create_row_sql(id, place_id, name, url, weekday, hour, expected, lat, lon,
                   address, location_type, main_category, main_category_weight, visit_duration, types, category):

    row_sql = f"""
INSERT INTO public.alpha_locations_expected(
    id,
    place_id,
    name, url,
    weekday, hour, expected,
    lat, lon, address,
    location_type,
    main_category, 
    main_category_weight,
    visit_duration,
    types, category)
VALUES(
    '{id}',
    '{place_id}',
    '{name}',
    '{url}',
    '{weekday}',
    '{hour}',
    '{expected}',
    '{lat}', '{lon}', '{address}', '{location_type}',
    '{main_category}', '{main_category_weight}',
    '{visit_duration}', '{types}', '{category}');
    """

    return row_sql


# def parse_alpha(datadir):
#     """Parser for ALPHA data."""
#
#     # Create database connection
#     db_int = DatabaseInteractions()
#     conn = db_int.get_sqlalchemy_connection()
#
#     # Load raw Alpha data dump from table
#     raw = pd.read_sql_table(f'google_raw_locations_expected_production', conn)  # << old table name
#     # raw = pd.read_sql_table('google_raw_locations_expected_production', conn)    # << new table name (all tables of new Alpha dump are empty)
#     logger.debug('alpha data %s', raw.shape)
#
#     # Create table for modified Alpha data
#     conn.execute(ModifyTables.create_alpha_table())
#     # Iterate over raw entries to fill new table
#     id_counter = 0
#     for i in range(0, len(raw)):
#         id_counter = parse_alpha_item(conn, i, id_counter, raw)
#         if i % 100 == 0:
#             logger.debug('row %d', id_counter)


# HOTFIX: onderstaande parser heeft betrekking op oude dump 'google_raw_feb.dump'. Deze aplpha parser is opgeschoond (zie code hierboven),
# maar die is niet werkend voor de oude dump. In de nieuwe dumps zit geen data.
def parse_alpha(datadir):
    """Parser for ALPHA data."""

    # def create_row_sql(id, place_id, name, url, weekday, hour, expected, lat, lon,
    #                    address, location_type, main_category, main_category_weight, visit_duration, types, category):
    #
    #     row_sql = '''INSERT INTO public.alpha_locations_expected(id, \
    #     place_id, name, url, weekday, hour, expected, lat, lon, address, \
    #     location_type, main_category, main_category_weight, visit_duration, types, category)
    #     VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
    #     ''' % (id, place_id, name, url, weekday, hour, expected, lat, lon, address,
    #            location_type, main_category, main_category_weight, visit_duration, types, category)
    #
    #     return row_sql

    # Create database connection
    db_int = DatabaseInteractions()
    conn = db_int.get_sqlalchemy_connection()

    # Load raw Alpha data dump from table
    raw = pd.read_sql_table('google_raw_locations_expected_acceptance', conn)  # << old table name
    # raw = pd.read_sql_table('google_raw_locations_expected_production', conn)    # << new table name (all tables of new Alpha dump are empty)

    # Create table for modified Alpha data
    conn.execute(ModifyTables.create_alpha_table())

    # Lambda function to double up quotation marks for sql writing.
    fix_quotes = lambda x: re.sub("'", "''", x)

    # Iterate over raw entries to fill new table
    id_counter = 0
    for i in range(0, len(raw)):
        place_id = raw.place_id[i]
        name = raw.name[i]
        url = raw.data[i]['url']
        weekday = raw.scraped_at[i].weekday()
        lat = raw.data[i]['location']['coordinates'][1]
        lon = raw.data[i]['location']['coordinates'][0]
        address = raw.data[i]['formatted_address']
        location_type = raw.data[i]['location']['type']
        main_category, main_category_weight = evaluate_tags(raw.data[i]['types'])
        visit_duration = raw.data[i]['VisitDuration']
        types = str(raw.data[i]['types'])
        category = raw.data[i]['Category']

        # Fix quotes for sql writing
        name = fix_quotes(name)
        url = fix_quotes(url)
        address = fix_quotes(address)
        location_type = fix_quotes(location_type)
        visit_duration = fix_quotes(visit_duration)
        types = fix_quotes(types)

        # Loop over all expected hour intervals for each location and scrape day
        for interval in raw.data[i]['Expected']:

            # Truncate time interval to first hour of the interval
            hour = interval['TimeInterval'][0:2]
            hour = int(re.sub("[^0-9]", "", hour))
            ampm = interval['TimeInterval'][1:4]
            ampm = re.sub('[^a-zA-Z]+', '', ampm)
            if ampm == 'pm':
                if hour == 12:
                    pass
                else:
                    hour += 12

            # Get the expected crowdedness value for this hour (relative value)
            expected = interval['ExpectedValue']

            # Create sql query to write data to database
            row_sql = create_row_sql(id_counter, place_id, name, url, weekday, hour, expected, lat, lon, address,
                                     location_type, main_category, main_category_weight, visit_duration,
                                     types, category)

            # Write data to database
            conn.execute(row_sql)

            # Update id counter so all rows have a unique id
            id_counter += 1
