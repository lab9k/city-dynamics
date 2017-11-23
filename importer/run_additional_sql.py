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

tables_to_modify = [config_src.get(x, 'TABLE_NAME') for x in config_src.sections() if config_src.get(x, 'CREATE_POINT') == 'YES']

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

  CREATE INDEX {1} ON "{0}" USING GIST(geom);
  """.format(tablename, 'geom_' + tablename)


def add_buurtcombinatie_query(table):
  return """
  SELECT "{0}".id, BUURTCOMBINATIE.Stadsdeel_code
  FROM "{0}", BUURTCOMBINATIE
  WHERE ST_Intersects("{0}".geom, BUURTCOMBINATIE.COORDS);
  """.format(table)

def test(table):
  return """
  SELECT 
  g.id as id,
  b."Buurtcombinatie" as bc
  FROM 
  gvb as g, 
  buurtcombinatie as b
  WHERE ST_Intersects(g.geom, b."COORDS")
  """


def dummy(table):
  return"""SELECT 
  e.*, 
  g.naam as gebiedsnaam, 
  g.code as gebiedscode
  INTO 
    crowscores_totaal
  FROM
     (SELECT 
       c.*, 
       d.stadsdeelcode,
       d.buurtcode,
       d.wijkcode,
       d.stadsdeelnaam,
       d.buurtnaam,
       d.wijknaam
    FROM 
      (select * from crowscores) as c, 
      (SELECT 
         a.stadsdeelcode,
         a.buurtcode,
         w.vollcode as wijkcode,
         a.stadsdeelnaam,
         a.buurtnaam,
         w.naam as wijknaam,
         a.wkb_geometry
       FROM
       (  SELECT 
          s.naam as stadsdeelnaam,
          s.code as stadsdeelcode,
          b.naam as buurtnaam,
          s.code || b.code as buurtcode,
          b.wkb_geometry
          FROM 
            buurt as b, 
            stadsdeel as s
          WHERE ST_WITHIN(ST_CENTROID(b.wkb_geometry),s.wkb_geometry)
        ) as a, 
        buurtcombinatie as w
      WHERE ST_WITHIN(ST_CENTROID(a.wkb_geometry),w.wkb_geometry)) as d
    WHERE ST_WITHIN(ST_CENTROID(c.geom), d.wkb_geometry)
    ) as e,
    gebiedsgerichtwerken as g
  WHERE ST_WITHIN(ST_CENTROID(e.geom), g.wkb_geometry);
  ALTER TABLE crowscores_totaal 
  ADD PRIMARY KEY (id);
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
    pg_str = get_pg_str(config_auth.get(dbConfig,'host'),config_auth.get(dbConfig,'port'),config_auth.get(dbConfig,'dbname'), config_auth.get(dbConfig,'user'), config_auth.get(dbConfig,'password'))
    for table in tables_to_modify:
        print(table)
        #execute_sql(pg_str, create_geometry_query(table))
        #print(add_buurtcombinatie_query(table))
        #execute_sql(pg_str, add_buurtcombinatie_query(table))
        execute_sql(pg_str, test(table))


if __name__ == '__main__':
    desc = "Run additional SQL."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('dbConfig', type=str, help='dev or docker', nargs=1)
    args = parser.parse_args()
    main(args.dbConfig[0])