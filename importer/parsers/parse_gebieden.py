from .parse_helper_functions import DatabaseInteractions
from .parse_helper_functions import LoadLayers
import logging

logger = logging.getLogger(__name__)

db_int = DatabaseInteractions()

def main():
    """Load 'stadsdeel' and 'buurtcombinatie' tables into database."""
    logger.debug('Parsing gebieden...')
    pg_str = db_int.get_postgresql_string()
    LoadLayers.load_layers(pg_str)
    logger.debug('...done')

if __name__ == "__main__":
    # Create database connection
    main()