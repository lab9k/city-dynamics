
from datetime import datetime
from datetime import timedelta
from datetime import timezone
# Packages
from rest_framework.test import APITestCase

from . import factories


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        'citydynamics/drukteindex',
    ]

    def setUp(self):
        stamp = datetime(2017, 1, 1, 1, 1, tzinfo=timezone.utc)
        one_hour = timedelta(seconds=3600)

        for i in range(1001):
            factories.DrukteindexFactory(
                timestamp=stamp,
            )
            stamp = stamp + one_hour

    def valid_html_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'text/html; charset=utf-8', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_index_pages(self):
        url = 'citydynamics'

        response = self.client.get('/{}/'.format(url))

        self.assertEqual(
            response.status_code,
            200, 'Wrong response code for {}'.format(url))

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.assertEqual(
                response.status_code,
                200, 'Wrong response code for {}'.format(url))

            self.assertEqual(
                response['Content-Type'], 'application/json',
                'Wrong Content-Type for {}'.format(url))

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))

            # self.assertNotEqual(
            #    response.data['count'],
            #    0, 'Wrong result count for {}'.format(url))

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))

            # self.assertNotEqual(
            #    response.data['count'],
            #    0, 'Wrong result count for {}'.format(url))
