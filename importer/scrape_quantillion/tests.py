"""
Some tests.
"""

import json
import unittest
from unittest import mock
import slurp_api
import models
import configparser

from models import Session

config_auth = configparser.RawConfigParser()
config_auth.read('../auth.conf')


class TestDB():

    def setUp(self):
        models.create_db()
        self.engine = models.make_engine(section='test')
        self.connection = self.engine.connect()
        self.testdatabase = config_auth.get('test', 'dbname')
        self.transaction = self.connection.begin()
        models.Base.metadata.create_all(bind=self.engine)
        models.set_session(self.engine)

    def tearDown(self):
        self.transaction.rollback()
        self.connection.close()
        self.engine.dispose()
        models.drop_db()


class TestDBWriting(TestDB, unittest.TestCase):
    """
    Test writing to database
    """

    @mock.patch('slurp_api.get_the_json')
    def test_live_locations(self, get_json_mock):

        with open('fixtures/realtime.json') as mockjson:
            test_json = json.loads(mockjson.read())

        get_json_mock.return_value = test_json
        slurp_api.locations_realtime()
        count = models.session.query(models.GoogleRawLocations).count()
        self.assertEqual(count, 1)
        # make sure we do not make duplicates
        slurp_api.locations_realtime()
        self.assertEqual(count, 1)
