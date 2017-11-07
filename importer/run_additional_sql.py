"""
This is where SQL queries that must be run after import go.
"""
import psycopg2
import configparser
import argparse

# parse authentication configuration
config = configparser.RawConfigParser()
config.read('auth.conf') # in docker
# config.read('importer/auth.conf') # local

createGeomGVB = """
ALTER TABLE "GVB"
  DROP COLUMN IF EXISTS id;
ALTER TABLE "GVB" 
  ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE "GVB"
  DROP COLUMN IF EXISTS geom;
ALTER TABLE "GVB"
  ADD COLUMN geom geometry;
UPDATE "GVB"
    SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);

CREATE INDEX geom_GVB ON "GVB" USING GIST(geom);
"""

createGeomMORA = """
ALTER TABLE "MORA"
  DROP COLUMN IF EXISTS id;
ALTER TABLE "MORA" 
  ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE "MORA"
  DROP COLUMN IF EXISTS geom;
ALTER TABLE "MORA"
  ADD COLUMN geom geometry;
UPDATE "MORA"
    SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);

CREATE INDEX geom_MORA ON "MORA" USING GIST(geom);
"""


def execute_sql(pg_str, sql):
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def get_pg_str(host, port, user, dbname, password):
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def main(dbConfig):
    print('Additional SQL run after import concludes.')
    pg_str = get_pg_str(config.get(dbConfig,'host'),config.get(dbConfig,'port'),config.get(dbConfig,'dbname'), config.get(dbConfig,'user'), config.get(dbConfig,'password'))
    execute_sql(pg_str, createGeomGVB)
    print('geometry field created in GVB')
    execute_sql(pg_str, createGeomMORA)
    print('geometry field created in MORA')


if __name__ == '__main__':
    desc = "Run additional SQL."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('dbConfig', type=str, help='dev or docker', nargs=1)
    args = parser.parse_args()
    main(args.dbConfig[0])