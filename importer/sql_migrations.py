import configparser
import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def get_conn(dbconfig):
    """Create a connection to the database."""
    postgres_url = URL(
        drivername='postgresql',
        username=config_auth.get(dbconfig, 'user'),
        password=config_auth.get(dbconfig, 'password'),
        host=config_auth.get(dbconfig, 'host'),
        port=config_auth.get(dbconfig, 'port'),
        database=config_auth.get(dbconfig, 'dbname')
    )
    conn = create_engine(postgres_url)
    return conn

create_hotpots = """CREATE TABLE public.datasets_hotspots
(
  index bigint NOT NULL,
  "Hotspot" text,
  "Latitude" double precision,
  "Longitude" double precision,
  point_sm geometry,
  CONSTRAINT datasets_hotspots_pkey PRIMARY KEY (index)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.datasets_hotspots
  OWNER TO citydynamics;

-- Index: public.datasets_hotspots_point_sm_id

-- DROP INDEX public.datasets_hotspots_point_sm_id;

CREATE INDEX datasets_hotspots_point_sm_id
  ON public.datasets_hotspots
  USING gist
  (point_sm);"""

create_hotpots_drukteindex = """CREATE TABLE public.datasets_hotspotsdrukteindex
(
  index bigint NOT NULL,
  hour integer NOT NULL,
  drukteindex double precision NOT NULL,
  hotspot_id bigint NOT NULL,
  CONSTRAINT datasets_hotspotsdrukteindex_pkey PRIMARY KEY (index),
  CONSTRAINT datasets_hotspotsdru_hotspot_id_fd4451d0_fk_datasets_ FOREIGN KEY (hotspot_id)
      REFERENCES public.datasets_hotspots (index) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.datasets_hotspotsdrukteindex
  OWNER TO citydynamics;

-- Index: public.datasets_hotspotsdrukteindex_hotspot_id_fd4451d0

-- DROP INDEX public.datasets_hotspotsdrukteindex_hotspot_id_fd4451d0;

CREATE INDEX datasets_hotspotsdrukteindex_hotspot_id_fd4451d0
  ON public.datasets_hotspotsdrukteindex
  USING btree
  (hotspot_id);"""

def main():
    log.debug("Creating empty tables for API..")

    conn = get_conn(dbconfig=args.dbConfig[0])
    conn.execute(create_hotpots)
    conn.execute(create_hotpots_drukteindex)

    log.debug("..done")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'dbConfig', type=str,
        help='database config settings: dev or docker',
        nargs=1)
    args = parser.parse_args()
    main()

