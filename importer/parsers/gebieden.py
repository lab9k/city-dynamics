from .helper_functions import DatabaseInteractions
from .helper_functions import LoadLayers
from .helper_functions import GeometryQueries
import logging

logger = logging.getLogger(__name__)

db_int = DatabaseInteractions()
conn = db_int.get_sqlalchemy_connection()


def run(conn, *_, **config):
    """Load 'stadsdeel' and 'buurtcombinatie' tables into database."""

    pg_str = db_int.get_postgresql_string()
    LoadLayers.load_layers(pg_str)
    conn.execute(GeometryQueries.simplify_polygon(
        'buurtcombinatie', 'wkb_geometry', 'wkb_geometry_simplified'))

    logger.info('...done!')
