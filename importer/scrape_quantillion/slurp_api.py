"""
Quantillion provides api with scraped data.

on
host: http://apis.quantillion.io
port: 3001
username: gemeenteAmsterdam

Development
host: http://apis.development.quantillion.io
port: 3001
username: gemeenteAmsterdam
ion
host: http://apis.quantillion.io
port: 3001
username: gemeenteAmsterdam

Development
host: http://apis.development.quantillion.io
port: 3001
username: gemeenteAmsterdam

"""

import requests
import os
import models
import logging


log = logging.getLogger(__name__)


api_config = {
    'password': os.getenv('QUANTILLION_PASSWORD'),
    'hosts': [
        'http://apis.quantillion.io',
        # 'http://apis.development.quantillion.io',
        # Production: 35.159.8.123
        'http://35.159.8.123',
        # Development: 18.196.227.0
        # '18.196.227.0',
    ],
    'port': 3001,
    'username': 'gemeenteAmsterdam',
}


auth = (api_config['username'], api_config['password'])


def get_the_json(endpoint, params={}, auth=auth):
    """
    Get some json of endpoint!

    try prod. fall back on acceptance
    """
    json = None
    response = None
    port = api_config['port']
    for host in api_config['hosts']:
        url = f'{host}:{port}/gemeenteamsterdam/{endpoint}'
        response = requests.get(url, params=params, auth=auth)
        if response.status_code == 200:
            break

    if response:
        json = response.json()

    return json


def locations_realtime():
    """
    Get latests locations with real-time data
    """
    endpoint = 'realtime'
    json = get_the_json(endpoint)
    session = models.session

    if not json:
        log.error('No data recieved')
        raise ValueError("No json data?!?")

    # store the location json!
    for loc in json:

        qa_id = loc['place_id']

        existing = (
            session
            .query(models.GoogleRawLocations)
            .filter_by(qa_id=qa_id)
        )

        if existing.count():
            log.debug('Already exists %s', qa_id)
            # already exists
            continue

        grj = models.GoogleRawLocations(
            qa_id=qa_id,
            name=loc['name'],
            data=loc,
        )
        session.add(grj)
        session.commit()


def locations_realtime_current():
    """
    Current realtime crowdness information
    """
    endpoint = 'realtime/current'
    json = get_the_json(endpoint)
    session = models.session

    if not json:
        log.error('No data recieved')
        raise ValueError("No json data?!?")

    # store the location json!
    for loc in json:
        qa_id = loc['place_id']
        pass




def expected_values():
    """
    """
    pass


def main():
    engine = models.make_engine(section='docker')
    # models.Base.metadata.create_all(engine)
    models.set_session(engine)

    # load the data!
    locations_realtime()


if __name__ == '__main__':
    main()

