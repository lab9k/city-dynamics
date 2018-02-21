"""
Quantillion provides api with scraped google data.

Production
host: http://apis.quantillion.io
port: 3001
username: gemeenteAmsterdam

Development
host: http://apis.development.quantillion.io
port: 3001
username: gemeenteAmsterdam
"""

import gevent
import grequests
# import requests
import os
import models
import logging

from gevent.queue import JoinableQueue
from dateutil import parser

from psycogreen.gevent import patch_psycopg
patch_psycopg()


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.ERROR)

ENVIRONMENT = os.getenv('ENVIRONMENT', 'acceptance')

WORKERS = 5

GET_QUEUE = JoinableQueue(maxsize=1500)

STATUS = {
    'done': False
}

LIMIT = 1000

PARAMS = {'limit': LIMIT}

api_config = {
    'password': os.getenv('QUANTILLION_PASSWORD'),
    'hosts': {
        'production': 'http://apis.quantillion.io',
        'acceptance': 'http://apis.development.quantillion.io',
        # Production: 35.159.8.123
        # 'http://35.159.8.123',
        # Development: 18.196.227.0
        # '18.196.227.0',
    },
    'port': 3001,
    'username': 'gemeenteAmsterdam',
}


AUTH = (api_config['username'], api_config.get('password'))


def get_the_json(endpoint, params={'limit': 1000}) -> list:
    """
    Get some json of endpoint!

    try prod. fall back on development
    """
    json = []
    response = None
    port = api_config['port']

    host = api_config['hosts'][ENVIRONMENT]

    url = f'{host}:{port}/gemeenteamsterdam/{endpoint}'

    async_r = grequests.get(url, params=params, auth=AUTH)
    gevent.sleep()
    gevent.spawn(async_r.send).join()

    response = async_r.response

    if response is None:
        log.error('RESPONSE NONE %s %s', url, params)
        return []
    elif response.status_code == 200:
        log.debug(f' OK  {response.status_code}:{url}')
    elif response.status_code == 500:
        log.debug(f'FAIL {response.status_code}:{url}')

    if response:
        json = response.json()

    return json


def add_locations_to_db(endpoint, json: list):
    """
    Given json api response, store data in database
    """

    if not json:
        log.error('No data recieved')
        return

    db_model = models.GoogleRawLocationsRealtime

    if endpoint == 'expected':
        db_model = models.GoogleRawLocationsExpected

    # make new session
    session = models.Session()

    log.debug(f"Storing {len(json)} locations")

    # Store the location json!
    for loc in json:

        place_id = loc['place_id']
        scraped_at = parser.parse(loc['ScrapeTime'])

        gevent.sleep()

        grj = db_model(
            place_id=place_id,
            scraped_at=scraped_at,
            name=loc['name'],
            data=loc,
        )

        session.add(grj)

    session.commit()

    log.debug(f"Updated {len(json)} locations")


def get_params():

    yield PARAMS

    while True:
        PARAMS['skip'] = PARAMS.get('skip', 0) + 1000
        yield PARAMS


def get_locations(work_id, endpoint):
    """
    Get locations with real-time data
    """
    gen_params = get_params()

    while True:
        log.debug(f'Next for {work_id}')
        params = next(gen_params)
        log.debug(params)
        json_response = get_the_json(endpoint, params)

        add_locations_to_db(endpoint, json_response)

        if len(json_response) < LIMIT:
            # We are done
            STATUS['done'] = True
            break

        # generate next step
        if STATUS.get('done'):
            break

    log.debug(f'Done {work_id}')


def run_workers(endpoint, workers=WORKERS, parralleltask=get_locations):
    """
    Run X workers processing search tasks
    """
    jobs = []

    STATUS['done'] = False

    for i in range(workers):
        jobs.append(
            gevent.spawn(parralleltask, i, endpoint)
        )

    with gevent.Timeout(3600, False):
        # waint untill all search tasks are done
        # but no longer than an hour
        gevent.joinall(jobs)


def main():
    engine = models.make_engine(section='docker')
    # models.Base.metadata.create_all(engine)
    models.set_engine(engine)

    # run_workers(get_locations, 'expected')
    # load the data!
    run_workers('realtime')
    #  locations_realtime()


if __name__ == '__main__':
    main()
