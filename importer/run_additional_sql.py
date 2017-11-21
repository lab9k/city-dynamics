"""
This is where SQL queries that must be run after import go.
"""
import psycopg2
import configparser
import argparse
import sys

# parse authentication configuration
config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf') 

config_src = configparser.RawConfigParser()
config_src.read('sources.conf') 

tables_to_modify = [config_src.get(x, 'TABLE_NAME') for x in config_src.sections() if config_src.get(x, 'CONTAINS_GEOM') == 'YES']

def create_geometry_query(tablename):
  return """
  ALTER TABLE "{0}"
    DROP COLUMN IF EXISTS id;
  ALTER TABLE "{0}" 
    ADD COLUMN id SERIAL PRIMARY KEY;
  ALTER TABLE "{0}"
    DROP COLUMN IF EXISTS geom;
  ALTER TABLE "{0}"
    ADD COLUMN geom geometry;
  UPDATE "{0}"
      SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);

  CREATE INDEX {1} ON "GVB" USING GIST(geom);
  """.format(tablename, 'geom_' + tablename)


def execute_sql(pg_str, sql):
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def get_pg_str(host, port, user, dbname, password):
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def main(dbConfig):
    pg_str = get_pg_str(config_auth.get(dbConfig,'host'),config_auth.get(dbConfig,'port'),config_auth.get(dbConfig,'dbname'), config_auth.get(dbConfig,'user'), config_auth.get(dbConfig,'password'))
    for table in tables_to_modify:
        execute_sql(pg_str, create_geometry_query(table))


if __name__ == '__main__':
    desc = "Run additional SQL."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('dbConfig', type=str, help='dev or docker', nargs=1)
    args = parser.parse_args()
    main(args.dbConfig[0])