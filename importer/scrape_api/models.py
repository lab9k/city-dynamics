import os
import logging
import argparse

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database

from settings import config_auth


ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

Base = declarative_base()

Session = sessionmaker()

session = []


def make_conf(section):

    host = config_auth.get(section, 'host')
    port = config_auth.get(section, 'port')
    db = config_auth.get(section, 'dbname')

    CONF = URL(
        drivername='postgresql',
        username=config_auth.get(section, 'user'),
        password=config_auth.get(section, 'password'),
        host=host,
        port=port,
        database=db,
    )

    log.info(f"Database config {host}:{port}:{db}")
    return CONF


def create_db(section='test'):
    CONF = make_conf(section)
    log.info(f"Created database")
    if not database_exists(CONF):
        create_database(CONF)


def drop_db(section='test'):
    log.info(f"Drop database")
    CONF = make_conf(section)
    if database_exists(CONF):
        drop_database(CONF)


def make_engine(section='docker'):
    CONF = make_conf(section)
    engine = create_engine(CONF)
    return engine


def set_engine(engine):
    global session
    Session.configure(bind=engine)
    # create a configured "session" object for tests
    session = Session()
    return session


class GoogleRawLocationsRealtime(Base):
    """
    Raw json location information realtime
    """
    __tablename__ = f'google_raw_locations_realtime_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    name = Column(String)
    data = Column(JSONB)


class GoogleRawLocationsExpected(Base):
    """
    Raw json location information of expected data
    """
    __tablename__ = f'google_raw_locations_expected_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    name = Column(String)
    data = Column(JSONB)


class ParkingLocation(Base):
    """
    Raw json proxy for api.
    """
    __tablename__ = f'parkinglocations_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    # place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    # name = Column(String)
    data = Column(JSONB)


class Events(Base):
    """
    Raw json proxy for api.
    """
    __tablename__ = f'eventlocations_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    # place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    # name = Column(String)
    data = Column(JSONB)


class TravelTime(Base):
    """
    Raw json proxy for api.
    """
    __tablename__ = f'traveltime_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    # place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    # name = Column(String)
    data = Column(JSONB)


class GoogleRawLocationsRealtimeCurrent(Base):
    """
    Raw json location information realtime
    """
    __tablename__ = f'google_raw_locations_realtime_current_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    name = Column(String)
    data = Column(JSONB)


class GoogleRawLocationsExpectedCurrent(Base):
    """
    Raw json location information expected
    """
    __tablename__ = f'google_raw_locations_expected_current_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    name = Column(String)
    data = Column(JSONB)


class GoogleLocations(Base):
    """
    Unique locations with proper bag_id / vestiging ids
    """
    __tablename__ = f'google_locations_{ENVIRONMENT}'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    bag_id = Column(Integer, unique=True)
    place_id = Column(String, index=True)
    scraped_at = Column(TIMESTAMP, index=True)
    name = Column(String)
    data = Column(JSONB)


if __name__ == '__main__':
    desc = "Manage google tables."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        '--drop',
        action='store_true',
        default=False,
        help="Drop existing")

    args = inputparser.parse_args()
    engine = make_engine()

    if args.drop:
        # resets everything
        log.warning('DROPPING ALL DEFINED TABLES')
        Base.metadata.drop_all(engine)

    log.warning('CREATING DEFINED TABLES')
    # recreate tables
    Base.metadata.create_all(engine)
    # create tables
