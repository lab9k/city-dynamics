# Packages
from rest_framework.test import APITestCase


class BrowseDatasetsTestCase(APITestCase):

    datasets = [
        'citydynamics/drukteindex',
    ]

    def setUp(self):
        # TODO add some test data!
        pass

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
