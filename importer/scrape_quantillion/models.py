import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Sequence
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database

import configparser


config_auth = configparser.RawConfigParser()
config_auth.read('../auth.conf')


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
    log.info(f"Created database")
    CONF = make_conf(section)
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


def set_session(engine):
    global session
    Session.configure(bind=engine)
    # create a configured "Session" class
    session = Session()


class GoogleRawLocations(Base):
    """
    Raw json location information
    """
    __tablename__ = 'google_raw_locations'
    id = Column(Integer, Sequence('grl_seq'), primary_key=True)
    qa_id = Column(String, index=True)
    name = Column(String)
    data = Column(JSON)


if __name__ == '__main__':
    # resets everything
    engine = make_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # create tables
