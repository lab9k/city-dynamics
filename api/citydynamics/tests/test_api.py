# Packages
from rest_framework.test import APITestCase

from . import factories


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        'api/buurtcombinatie',
        'api/realtime',
        'api/hotspots',
    ]

    def setUp(self):
        self.h = factories.HotspotsFactory()

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
        url = 'api'

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

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))

    def test_druktecijfers_in_hotspots(self):
        url = f"api/hotspots/{self.h.index}"
        response = self.client.get('/{}/'.format(url))

        self.assertIn(
            'druktecijfers',
            response.data,
            'Missing druktecijfers attribute in {}'.format(url))

        url = "/api/hotspots/"
        response = self.client.get(url)
        self.assertIn(
            'druktecijfers',
            response.data['results'][0],
            'Missing druktecijfers attribute in {}'.format(url))
