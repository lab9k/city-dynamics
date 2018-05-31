

import logging
import re
import pandas as pd

from ETLFunctions import DatabaseInteractions
from ETLFunctions import ModifyTables


logger = logging.getLogger(__name__)


categories_tags_mapping = {
    'default': [
        'alles_wat_geen_andere_tag_heeft', 'storage',
        'synagogue', 'church', 'place_of_worship',
        'spa', 'gym'],
    'park': ['park'],
    'ov': [
        'train_station', 'subway_station', 'bus_station',
        'transit_station'],
    'museum': ['museum'],
    'bar': [
        'bowling_alley', 'casino', 'movie_theatre',
        'night_club', 'bar', 'cafe'],
    'restaurant': ['meal_takeaway', 'restaurant'],
    'supermarket': [
        'markt_winkelcentrum', 'supermarket',
        'grocery_or_supermarket'],
    'store': [
        'beauty_salon', 'laundry', 'bicycle_store',
        'hardware_store', 'jewelry_store',
        'shopping_mall', 'art_gallery', 'liquor_store',
        'car_dealer', 'pharmacy', 'department_store',
        'shoe_store', 'convenience_store', 'furniture_store',
        'electronics_store', 'book_store',
        'gas_station', 'clothing_store', 'bakery',
        'home_goods_store', 'store'],

    'service': [
        'school', 'local_government_office', 'lawyer',
        'post_office', 'accounting',
        'real_estate_agency', 'veteranian_care',
        'hospital', 'general_contractor', 'library',
        'travel_agency', 'meal_delivery', 'car_wash',
        'hair_care', 'physiotherapist', 'car_rental',
        'bank', 'car_repair', 'dentist', 'finance', 'doctor'],

    'disregard': [
        'point_of_interest', 'establishment', 'food',
        'health', 'atm']
}

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
    # Set weight to -1, since other categories need
    # to be allowed to overwrite the default category.
    main_category = 'default'
    main_category_weight = -1

    # Assign categories to locations based on tags.
    # Only keep the category-tag/weight for the tag with the highest weight.
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


def create_row_sql(
        id, place_id, name, url, weekday, hour, expected, lat, lon,
        address, location_type, main_category,
        main_category_weight, visit_duration, types, category):

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
    main_category, main_category_weight = evaluate_tags(
        str(raw.data[i]['types']))
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

    # logger.debug(raw.data[i]['Expected'])

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
        row_sql = create_row_sql(
            id_counter, place_id, name, url, weekday, hour,
            expected, lat, lon, address,
            location_type, main_category,
            main_category_weight, visit_duration, types, category)

        # Write data to database
        conn.execute(row_sql)

        # Update id counter so all rows have a unique id
        id_counter += 1

        if id_counter % 100 == 0:
            logger.debug('alpha %s', id_counter)

    return id_counter


def parse(datadir):
    """Parser for ALPHA data."""

    # Toggle to use the old file "google_raw_feb.dump".
    # This is our fallback when Quantillion scraper fails.
    # Also change pg_restore line in files "run_index.sh"
    # and "deploy/import/import.sh".
    use_old_dump = True

    # Create database connection
    db_int = DatabaseInteractions()
    conn = db_int.get_sqlalchemy_connection()

    # Load raw Alpha data dump from table
    tablename = "google_raw_locations_expected_production"
    if use_old_dump:
        tablename = "google_raw_locations_expected_acceptance"
    raw = pd.read_sql_table(tablename, conn)

    # logger.debug('alpha data %s', raw.shape)

    # Create table for modified Alpha data
    conn.execute(ModifyTables.create_alpha_table())
    # Iterate over raw entries to fill new table
    id_counter = 0
    for i in range(0, len(raw)):
        id_counter = parse_alpha_item(conn, i, id_counter, raw)
        if i % 100 == 0:
            logger.debug('row %d', id_counter)
