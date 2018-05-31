import os
import pandas as pd
import logging
from .parse_helper_functions import DatabaseInteractions
from .parse_helper_functions import GeometryQueries

logger = logging.getLogger(__name__)

def main(datadir, conn, folder='hotspots'):
    """Parser for hotspots definition file."""
    logger.debug('Parsing hotspots table..')

    folder_path = os.path.join(datadir, folder)
    path = os.path.join(folder_path, 'hotspots_dev.csv')
    df = pd.read_csv(path)

    table_name = 'hotspots'
    df.to_sql(table_name, con=conn, if_exists='replace')

    conn.execute(GeometryQueries.convert_str_polygon_to_geometry(table_name))

    logger.debug('.. done')

if __name__ == "__main__":
    # Create database connection
    db_int = DatabaseInteractions()
    conn = db_int.get_sqlalchemy_connection()
    main(conn)
