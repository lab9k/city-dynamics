from .parse_helper_functions import DatabaseInteractions
from .parse_helper_functions import LoadLayers
from .parse_helper_functions import GeometryQueries
import logging

logger = logging.getLogger(__name__)

db_int = DatabaseInteractions()
conn = db_int.get_sqlalchemy_connection()


def run(conn, *_, **config):
    """Load 'stadsdeel' and 'buurtcombinatie' tables into database."""

    logger.info('Parsing gebieden...')

    pg_str = db_int.get_postgresql_string()
    LoadLayers.load_layers(pg_str)
    conn.execute(GeometryQueries.simplify_polygon(
        'buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))

    logger.info('...done!')
