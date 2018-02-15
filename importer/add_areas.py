"""
This is where SQL queries that must be run after import go.
"""
import psycopg2
import configparser
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# parse authentication configuration
config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

tables_to_modify = [config_src.get(x, 'TABLE_NAME') for x in config_src.sections() if
                    config_src.get(x, 'CREATE_POINT') == 'YES' ]


def create_geometry_query(tablename):
    return """
  ALTER TABLE "{0}"
    DROP COLUMN IF EXISTS geom;
  ALTER TABLE "{0}"
    ADD COLUMN geom geometry;
  UPDATE "{0}"
      SET geom = ST_PointFromText('POINT('||"lon"::double precision||' '||"lat"::double precision||')', 4326);
  CREATE INDEX {1} ON "{0}" USING GIST(geom);
  """.format(tablename, 'geom_' + tablename)


def simplify_polygon(table):
    return """
  ALTER TABLE "{0}"
    DROP COLUMN IF EXISTS wkb_geometry_simplified;
  ALTER TABLE "{0}"
    ADD COLUMN wkb_geometry_simplified geometry;
  UPDATE "{0}"
    SET wkb_geometry_simplified = ST_SimplifyPreserveTopology(wkb_geometry, 0.0001);
  """.format(table)


def add_bc_codes(table):
    return """
  DROP TABLE IF EXISTS "{0}";
  create
  table
    public."{0}" as with bc as(
      select
        *
      from
        buurtcombinatie
    ) select
      "{1}".*,
      bc."vollcode",
      bc."naam",
      LEFT(bc."vollcode", 1) as "stadsdeel_code"
    from
      public."{1}" join bc on
      st_intersects(
        "{1}".geom,
        bc.wkb_geometry
      )
  """.format(table + '_with_bc', table)


def set_primary_key(table):
    return """
  ALTER TABLE "{}" ADD PRIMARY KEY (index)
  """.format(table)


def execute_sql(pg_str, sql):
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def get_pg_str(host, port, user, dbname, password):
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def main(dbConfig, datasets):
    pg_str = get_pg_str(config_auth.get(dbConfig, 'host'), config_auth.get(dbConfig, 'port'),
                        config_auth.get(dbConfig, 'dbname'), config_auth.get(dbConfig, 'user'),
                        config_auth.get(dbConfig, 'password'))
    execute_sql(pg_str, simplify_polygon('buurtcombinatie'))

    for dataset in datasets:
        table_name = config_src.get(dataset, 'TABLE_NAME')
        logger.info('Handling {} table'.format(table_name))
        execute_sql(pg_str, create_geometry_query(table_name))
        execute_sql(pg_str, add_bc_codes(table_name))
        execute_sql(pg_str, set_primary_key(table_name + '_with_bc'))


if __name__ == '__main__':
    desc = "Run additional SQL."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('dbConfig', type=str, help='dev or docker', nargs=1)
    parser.add_argument('dataset', nargs='?', help="Upload specific dataset")
    args = parser.parse_args()

    p_datasets = config_src.sections()

    datasets = []

    for x in p_datasets:
        if config_src.get(x, 'ENABLE') == 'YES':
            if config_src.get(x, 'CREATE_POINT') == 'YES':
                datasets.append(x)

    if args.dataset:
        datasets = [args.dataset]

    main(args.dbConfig[0], datasets)
