"""
This module contains functions which are used a lot in the ETL process of the importer.
(ETL = Extraction, Transformation, Load)

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

    def __init__(self):
        config_auth = configparser.RawConfigParser()
        config_auth.read('auth.conf')
        config_section = 'database'

        self.host = config_auth.get(config_section, 'host')
        self.port = config_auth.get(config_section, 'port')
        self.database = config_auth.get(config_section, 'dbname')
        self.user = config_auth.get(config_section, 'user')
        self.password = config_auth.get(config_section, 'password')

    def get_postgresql_string(self):
        return 'PG:host={} port={} user={} dbname={} password={}'.format(
            self.host, self.port, self.user, self.database, self.password)

    def execute_sql(self, sql):
        with psycopg2.connect(self.pg_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

    def get_sqlalchemy_connection(self):
        """Create a connection to the database."""
        postgres_url = URL(
            drivername='postgresql',
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
        conn = create_engine(postgres_url)
        return conn


class ModifyTables(DatabaseInteractions):

    def __init__(self):
        GEOMETRY_POINT_NAME = "geom"  # name of our point geometry on table
        GEOMETRY_POLY_NAME = "polygon"  # name of our poly geometry on table

    @staticmethod
    def set_primary_key(tableName):
        return """
        ALTER TABLE "{}" ADD PRIMARY KEY (index)
        """.format(tableName)


    def table_has_point(self, tableName):
        sql = """
        SELECT EXISTS (SELECT 1
        FROM    information_schema.columns
        WHERE   table_schema='public'
        AND     table_name='{0}'
        AND     column_name='{1}');
        """.format(tableName, self.GEOMETRY_POINT_NAME)

        r = super().execute_sql()
        return r

    @staticmethod
    def create_geometry_column(tableName):
        return """
      ALTER TABLE "{0}"
        DROP COLUMN IF EXISTS geom;
      ALTER TABLE "{0}"
        ADD COLUMN geom geometry;
      UPDATE "{0}"
          SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);
      CREATE INDEX {1} ON "{0}" USING GIST(geom);
      """.format(tableName, 'geom_' + tableName)

    @staticmethod
    def simplify_polygon(tableName, original_column, simplified_column):
        return f"""
        ALTER TABLE             "{tableName}"
        DROP COLUMN IF EXISTS   "{simplified_column}";
        ALTER TABLE             "{tableName}"
        ADD COLUMN              "{simplified_column}" geometry;
        UPDATE                  "{tableName}"
        SET wkb_geometry_simplified = ST_SimplifyPreserveTopology("{original_column}", 0.0001);
        """.format(tableName, original_column, simplified_column)

    @staticmethod
    def add_vollcodes(tableName):
        return """
        ALTER TABLE             "{0}"
        DROP COLUMN IF EXISTS   vollcode;

        ALTER TABLE "{0}" add vollcode varchar;

        UPDATE "{0}" SET vollcode = buurtcombinatie.vollcode
        FROM buurtcombinatie
        WHERE st_intersects("{0}".geom, buurtcombinatie.wkb_geometry)
        """.format(tableName)

    @staticmethod
    def add_stadsdeelcodes(tableName):
        return """
        ALTER TABLE             "{0}"
        DROP COLUMN IF EXISTS   stadsdeelcode;

        ALTER TABLE "{0}" add stadsdeelcode varchar;

        UPDATE "{0}" SET stadsdeelcode = stadsdeel.code
        FROM stadsdeel
        WHERE st_intersects("{0}".geom, stadsdeel.wkb_geometry)
        """.format(tableName)

    @staticmethod
    def add_hotspot_names(tableName):
        return """
        ALTER table "{0}"
        DROP COLUMN IF EXISTS hotspot;

        ALTER TABLE "{0}" add hotspot varchar;

        UPDATE "{0}"
        SET hotspot = hotspots."hotspot"
        FROM hotspots
        WHERE st_intersects(ST_Buffer( CAST(hotspots.geom AS geography), 200.0), alpha_locations_expected.geom);
        """.format(tableName)

    @staticmethod
    def create_alpha_table():
        return """
        DROP TABLE IF EXISTS  public.alpha_locations_expected;

        CREATE TABLE  public.alpha_locations_expected(
            id              INTEGER,
            place_id        VARCHAR,
            name            TEXT,
            url             TEXT,
            weekday         INT4,
            hour            INT4,
            expected        FLOAT8,
            lat             FLOAT8,
            lon             FLOAT8,
            address         TEXT,
            location_type   TEXT,
            visit_duration  TEXT,
            types           TEXT,
            category        INT4);
        """


class LoadGebieden:
    """
    This class contains functionality to read geometrical
    information on areas in Amsterdam from a webservice
    """

    class NonZeroReturnCode(Exception):
        pass

    @classmethod
    def scrub(self, l):
        out = []
        for x in l:
            if x.strip().startswith('PG:'):
                out.append('PG: <CONNECTION STRING REDACTED>')
            else:
                out.append(x)
        return out

    @classmethod
    def run_command_sync(self, cmd, allow_fail=False):
        logging.debug('Running %s', self.scrub(cmd))

        retry = 0

        while retry < 5:
            p = subprocess.Popen(cmd)
            p.wait()
            if p.returncode != 0:
                logging.debug(
                    'Serive failed. Retry %d %s',
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
        cmd = [
            'ogr2ogr', '-overwrite', '-t_srs', 'EPSG:4326',
            '-nln', layer_name, '-F', 'PostgreSQL', pg_str, url]
        self.run_command_sync(cmd)

    @staticmethod
    def load_gebieden(pg_str):
        GEBIEDEN_WFS = "https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&SERVICE=wfs&Version=2.0.0&SRSNAME="  # noqa
        areaNames = [
            'stadsdeel', 'buurt',
            'buurtcombinatie', 'gebiedsgerichtwerken']

        srsName = 'EPSG:4326'
        for areaName in areaNames:
            WFS = GEBIEDEN_WFS + srsName + "&typename=" + areaName
            LoadGebieden.wfs2psql(WFS, pg_str, areaName)
            logger.info(areaName + ' loaded into PG.')
