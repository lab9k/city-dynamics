# Packages
from rest_framework.test import APITestCase
from . import factories


class BrowseDatasetsTestCase(APITestCase):

    all_endpoints = [
        'api/buurtcombinatie',
        'api/buurtcombinatie_drukteindex',
        'api/hotspots',
        'api/realtime',
        'api/historian'
    ]

    druktecijfers_endpoints = [
        '/api/buurtcombinatie_drukteindex/',
        '/api/hotspots/',
        '/api/historian/',
    ]

    def setUp(self):
        self.h = factories.HotspotsFactory()
        self.b = factories.BuurtcombinatieFactory()
        self.bi = factories.BuurtcombinatieIndexFactory(
            vollcode=self.b
        )

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
        for url in self.all_endpoints:
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
        for url in self.all_endpoints:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))

    # #TODO: debug
    def test_druktecijfers(self):
        for url in self.druktecijfers_endpoints:
            response = self.client.get(url)
            self.assertIn(
                'count', response.data,
                'Missing items attribute in {}'.format(url))
