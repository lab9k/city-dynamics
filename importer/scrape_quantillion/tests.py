"""
Some tests.
"""

import logging
import json
import unittest
from unittest import mock
import slurp_api
import models
import configparser

config_auth = configparser.RawConfigParser()
config_auth.read('../auth.conf')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)




transaction = []
connection = []
engine = []
session = []


def setUpModule():
    global transaction, connection, engine, session
    models.create_db()
    engine = models.make_engine(section='test')
    connection = engine.connect()
    transaction = connection.begin()
    models.Base.metadata.create_all(bind=engine)
    session = models.set_engine(engine)


def tearDownModule():
    log.debug('teardown')
    global transaction, connection, engine
    transaction.rollback()
    connection.close()
    engine.dispose()
    models.drop_db()


class TestDBWriting(unittest.TestCase):
    """
    Test writing to database
    """

    @mock.patch('slurp_api.get_the_json')
    def test_expected_locations(self, get_json_mock):

        slurp_api.STATUS['done'] = False
        with open('fixtures/expected.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.return_value = test_json

        slurp_api.get_locations('test', 'expected')
        count = session.query(
            models.GoogleRawLocationsExpected).count()
        self.assertEqual(count, 1)

    @mock.patch('slurp_api.get_the_json')
    def test_realtime_locations(self, get_json_mock):
        slurp_api.STATUS['done'] = False

        with open('fixtures/realtime.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.return_value = test_json

        slurp_api.get_locations('test', 'realtime')
        count = session.query(
            models.GoogleRawLocationsRealtime).count()
        self.assertEqual(count, 1)
