"""
Some tests.
"""

import json
import unittest
from unittest import mock
import slurp_api
import models
from settings import BASE_DIR


FIX_DIR = BASE_DIR + '/scrape_api'

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
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = models.set_engine(engine)


def tearDownModule():
    global transaction, connection, engine, session
    transaction.rollback()
    session.close()
    engine.dispose()
    connection.close()
    models.drop_db()


class TestDBWriting(unittest.TestCase):
    """
    Test writing to database
    """

    @mock.patch('slurp_api.get_the_json')
    def test_expected_locations(self, get_json_mock):

        with open(FIX_DIR + '/fixtures/expected.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.return_value = test_json

        slurp_api.run_workers('qa_expected', workers=1)
        count = session.query(models.GoogleRawLocationsExpected).count()
        self.assertEqual(count, 2)
        # make sure we do not make duplicates
        slurp_api.run_workers('qa_expected', workers=1)
        count = session.query(models.GoogleRawLocationsExpected).count()
        self.assertEqual(count, 2)

    @mock.patch('slurp_api.get_the_json')
    def test_realtime_locations(self, get_json_mock):

        with open(FIX_DIR + '/fixtures/realtime.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.return_value = test_json

        # slurp_api.get_locations('test', 'realtime')
        slurp_api.run_workers('qa_realtime', workers=1)

        count = session.query(models.GoogleRawLocationsRealtime).count()

        self.assertEqual(count, 1)
        # make sure we do not make duplicates
        slurp_api.run_workers('qa_realtime', workers=1)
        count = session.query(models.GoogleRawLocationsRealtime).count()
        self.assertEqual(count, 1)
