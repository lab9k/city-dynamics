import os
import pandas as pd
import logging
from .parse_helper_functions import DatabaseInteractions

logger = logging.getLogger(__name__)


def parse_parkeer_timeslot(path_to_dir, file):
    day_mapping = {
        'Ma': 0,
        'Tu': 1,
        'We': 2,
        'Th': 3,
        'Fr': 4,
        'Sa': 5,
        'Su': 6
    }

    day_str = file[9:11]
    day_nr = day_mapping[day_str]
    start_hour = int(file[12:14])
    end_hour = int(file[15:17])
    hour_range = list(range(start_hour, end_hour + 1))
    df_temp_all_hours = pd.DataFrame()
    df_temp = pd.read_csv(os.path.join(path_to_dir, file))
    df_temp['weekday'] = day_nr
    for hour in hour_range:
        df_temp['hour'] = hour
        df_temp_all_hours = pd.concat([df_temp_all_hours, df_temp])

    return df_temp_all_hours


def add_geometries(conn, *_, **config):
    pass
    # table_name = config['TABLE_NAME']
    # conn.execute(GeometryQueries.lon_lat_to_geom(table_name))
    # conn.execute(GeometryQueries.join_vollcodes(table_name))
    # conn.execute(GeometryQueries.join_stadsdeelcodes(table_name))
    # conn.execute(GeometryQueries.join_hotspot_names(table_name))


def run(conn, data_root, **config):
    """Parser for PARKEER data."""

    path_to_dir = os.path.join(data_root, config['OBJSTORE_CONTAINER'],
                                    config['DATA_FOLDER'])
    files = os.listdir(path_to_dir)

    week_number = 16
    files_in_week_number = []

    # TODO: Turn into regex to create "files_in_week_number" list
    for filename in files:
        if '2018_w{}'.format(week_number) in filename:
            if 'BETAALDP.csv' in filename:
                if 'Ma_Fr' not in filename:
                    if 'Sa_Su' not in filename:
                        files_in_week_number.append(filename)

    df_week = pd.DataFrame()

    for file in files_in_week_number:
        df_timeslot = parse_parkeer_timeslot(path_to_dir, file)
        df_week = pd.concat([df_week, df_timeslot])


    # print(df_week.columns.tolist())
    df_week['occupancy_times_vakken'] = df_week['occupancy'] * \
                                        df_week['vakken']
    df_week['vollcode'] = df_week.code.str[0:3]

    logger.info('Writing data to database...')
    table_name = config['TABLE_NAME']
    df_week.to_sql(table_name, con=conn, if_exists='replace')
    logger.info('...done')


    # determine_centroid_query = """
    #     ALTER
    #     geometry
    #     ST_Centroid(geometry
    #     g1);
    # """
    #
    # conn.execute(determine_centroid_query)
    #
    #
    # # UPDATE
    # # polygon_layer
    # # SET
    # # longitude = ST_X(ST_Centroid(geom)), Latitude = ST_Y(ST_Centroid(geom));