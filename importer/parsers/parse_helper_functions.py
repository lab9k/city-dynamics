"""
Contains commonly used functions which are used a lot
in the ETL process of the importer.
(ETL = Extraction, Transformation, Load)

#REFACTOR: module needs refactoring.

Contains several functions to work with database tables:
    - Create database connections
    - Transform, add, enrich tables etc.
"""

import time
import psycopg2
import configparser
import logging
import subprocess

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInteractions:
    """
    Implements several common interactions with the database
    """

    def __init__(self):
        """Initialization of a database interaction class instance."""
        config_auth = configparser.RawConfigParser()
        config_auth.read('auth.conf')
        config_section = 'database'

        self.host = config_auth.get(config_section, 'host')
        self.port = config_auth.get(config_section, 'port')
        self.database = config_auth.get(config_section, 'dbname')
        self.user = config_auth.get(config_section, 'user')
        self.password = config_auth.get(config_section, 'password')

    def get_postgresql_string(self):
        """Create and return a generic string to use as
        (commandline-)arguments to connect with database."""
        return 'PG:host={} port={} user={} dbname={} password={}'.format(
            self.host, self.port, self.user, self.database, self.password)

    def execute_sql(self, sql):
        """Execute a provided string of SQL code."""
        with psycopg2.connect(self.pg_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

    def get_sqlalchemy_connection(self):
        """Create a SQL database connection using the
        credentials provided in the class instance properties."""
        postgres_url = URL(
            drivername='postgresql',
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
        conn = create_engine(postgres_url).connect()
        return conn


class GeometryQueries:
    """The functions in this class allow the modification of tables

    Modification steps the functions in this class can conduct:
    - Changing the table's primary key
    - Checking whether a column exists in a given table
    - Creating a table for the alpha datasource
    - Adding geometry column
    - Adding vollcode column
    - Adding stadsdeelcode column
    - Adding hotspots column
    - Simplifying polygons in polygon column
    """

    def __init__(self):
        # not used?
        pass
        # GEOMETRY_POINT_NAME = "geom"    # name of our point geometry on table
        # GEOMETRY_POLY_NAME = "polygon"  # name of our poly geometry on table

    @staticmethod
    def set_primary_key(table_name):
        return """
        ALTER TABLE "{}" ADD PRIMARY KEY (index)
        """.format(table_name)

    def check_column_existence(self, table_name, column_name):
        sql = """
        SELECT EXISTS (SELECT 1
        FROM    information_schema.columns
        WHERE   table_schema='public'
        AND     table_name='{0}'
        AND     column_name='{1}');
        """.format(table_name, column_name)

        result = super().execute_sql(sql)
        return bool(result)

    @staticmethod
    def lon_lat_to_geom(table_name):
        return """
        ALTER TABLE "{0}"
        DROP COLUMN IF EXISTS geom;
        ALTER TABLE "{0}"
        ADD COLUMN geom geometry;
        UPDATE "{0}"
        SET geom = ST_PointFromText(
            'POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);
        CREATE INDEX {1} ON "{0}" USING GIST(geom);
        """.format(table_name, 'geom_' + table_name)   # noqa

    @staticmethod
    def convert_str_polygon_to_geometry(table_name):
        return """
        ALTER TABLE "{0}"
        ALTER COLUMN polygon
        TYPE Geometry USING polygon::Geometry;
        """.format(table_name)

    @staticmethod
    def simplify_polygon(table_name, original_column, simplified_column):
        return f"""
        ALTER TABLE             "{table_name}"
        DROP COLUMN IF EXISTS   "{simplified_column}";
        ALTER TABLE             "{table_name}"
        ADD COLUMN              "{simplified_column}" geometry;
        UPDATE                  "{table_name}"
        SET wkb_geometry_simplified = ST_SimplifyPreserveTopology("{original_column}", 0.0001);
        """.format(table_name, original_column, simplified_column)    # noqa

    @staticmethod
    def join_vollcodes(table_name):
        return """
        ALTER TABLE             "{0}"
        DROP COLUMN IF EXISTS   vollcode;

        ALTER TABLE "{0}" add vollcode varchar;

        UPDATE "{0}" SET vollcode = buurtcombinatie.vollcode
        FROM buurtcombinatie
        WHERE st_intersects("{0}".geom, buurtcombinatie.wkb_geometry)
        """.format(table_name)

    @staticmethod
    def join_stadsdeelcodes(table_name):
        return """
        ALTER TABLE             "{0}"
        DROP COLUMN IF EXISTS   stadsdeelcode;

        ALTER TABLE "{0}" add stadsdeelcode varchar;

        UPDATE "{0}" SET stadsdeelcode = stadsdeel.code
        FROM stadsdeel
        WHERE st_intersects("{0}".geom, stadsdeel.wkb_geometry)
        """.format(table_name)

    @staticmethod
    def join_hotspot_names(table_name):
        return """
            ALTER table "{0}"
            DROP COLUMN IF EXISTS hotspot;

            ALTER TABLE "{0}" add hotspot varchar;

            UPDATE "{0}"
            SET hotspot = hotspots."hotspot"
            FROM hotspots
            WHERE st_intersects(ST_Buffer( CAST(hotspots.polygon AS geography), 50.0), "{0}".geom);
        """.format(table_name)


class LoadLayers:
    """
    This class contains functionality to read geometrical
    information on areas in Amsterdam from a webservice.

    The following tables are requested and stored in the database:
        - stadsdeel
        - buurtcombinatie
    """

    class NonZeroReturnCode(Exception):
        """Used for subprocess error messages."""
        pass

    @classmethod
    def scrub(self, l):
        """Hide the login credentials of Postgres in the console."""
        out = []
        for x in l:
            if x.strip().startswith('PG:'):
                out.append('PG: <CONNECTION STRING REDACTED>')
            else:
                out.append(x)
        return out

    @classmethod
    def run_command_sync(self, cmd, allow_fail=False):
        """
        Run a string in the command line. Auto-retry up
        to 5 times when execution fails.

        Args:
            1. cmd: command line code formatted as a list::
                ['ogr2ogr', '-overwrite', '-t_srs',
                'EPSG:28992','-nln',layer_name,'-F' ,
                'PostgreSQL' ,pg_str ,url]
            2. Optional: allow_fail: True or false to return error code

        Returns:
            Excuted program or error message.
        """
        logging.debug('Running %s', self.scrub(cmd))

        retry = 0

        while retry < 5:
            p = subprocess.Popen(cmd)
            p.wait()
            if p.returncode != 0:
                logging.debug(
                    'Service failed. Retry %d %s',
                    retry, self.scrub(cmd))
                time.sleep(10)
                retry += 1
            else:
                # done. we got the data!
                break

        if p.returncode != 0 and not allow_fail:
            raise self.NonZeroReturnCode

        return p.returncode

    @classmethod
    def wfs2psql(self, url, pg_str, layer_name, **kwargs):
        """Command line ogr2ogr string to load a WFS into PostGres."""
        cmd = [
            'ogr2ogr', '-overwrite', '-t_srs', 'EPSG:4326',
            '-nln', layer_name, '-F', 'PostgreSQL', pg_str, url]
        self.run_command_sync(cmd)

    @staticmethod
    def load_layers(pg_str):
        """
        Load layers into Postgres using a list of titles of
        each layer within the WFS service.
        Args:
            pg_str: psycopg2 connection string::
            'PG:host= port= user= dbname= password='
        Returns:
            Loaded layers into postgres using ogr2ogr.
        """
        WFS_base = "https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&SERVICE=wfs&Version=2.0.0&SRSNAME="  # noqa
        layerNames = ['stadsdeel', 'buurtcombinatie']

        srsName = 'EPSG:4326'
        for layerName in layerNames:
            WFS = WFS_base + srsName + "&typename=" + layerName
            LoadLayers.wfs2psql(WFS, pg_str, layerName)
            logger.info(layerName + ' loaded into PG.')
