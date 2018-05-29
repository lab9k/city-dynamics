import os
import pandas as pd
import logging
from .parse_helper_functions import DatabaseInteractions

logger = logging.getLogger(__name__)

def main(datadir, conn):
    """Parser for hotspots definition file."""
    logger.debug('Parsing hotspots table..')
    path = os.path.join(datadir, 'hotspots_dev.csv')
    df = pd.read_csv(path)
    df.to_sql('hotspots', con=conn, if_exists='replace')
    logger.debug('.. done')

if __name__ == "__main__":
    # Create database connection
    db_int = DatabaseInteractions()
    conn = db_int.get_sqlalchemy_connection()
    main(conn)
