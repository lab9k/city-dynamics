import os
import pandas as pd
import logging
from .helper_functions import GeometryQueries

logger = logging.getLogger(__name__)


def add_geometries(conn, *_, **config):
    table_name = config['TABLE_NAME']
    conn.execute(GeometryQueries.convert_str_polygon_to_geometry(table_name))
    conn.execute(GeometryQueries.determine_centroid(table_name, geometry_column='polygon'))
    conn.execute(GeometryQueries.join_vollcodes(table_name, geometry_column='centroid'))
    conn.execute(GeometryQueries.join_stadsdeelcodes(table_name, geometry_column='centroid'))


def run(conn, data_root, **config):
    """Parser for hotspots definition file."""

    # Create dataframe from hotspots file.
    folder_path = os.path.join(data_root, config['OBJSTORE_CONTAINER'])
    path = os.path.join(folder_path, config['FILENAME'])
    df = pd.read_csv(path)

    # Write dataframe table to database (in Docker container).
    df.to_sql(config['TABLE_NAME'], con=conn, if_exists='append')
