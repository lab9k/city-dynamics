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
import datetime
import grequests
from settings import LIMIT
import os
import models
import logging
import argparse
import settings
import os.path

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

ENDPOINTS = [
    'realtime',
    'expected',
    'realtime/current',
    'expected/current',
]

ENDPOINT_MODEL = {
    'realtime': models.GoogleRawLocationsRealtime,
    'expected': models.GoogleRawLocationsExpected,
    'realtime/current': models.GoogleRawLocationsRealtimeCurrent,
    # 'expected/current': models.GoogleRawLocationsExpectedCurrent,
}

ENDPOINT_URL = {
    'realtime': '{host}:{port}/gemeenteamsterdam/{endpoint}/timerange',
    'expected': '{host}:{port}/gemeenteamsterdam/{endpoint}/timerange',
    'realtime/current': '{host}:{port}/gemeenteamsterdam/{endpoint}',
    # 'expected/current':
}


api_config = {
    'password': os.getenv('QUANTILLION_PASSWORD'),
    'hosts': {
        'production': 'http://apis.quantillion.io',
        'acceptance': 'http://apis.quantillion.io',
        #'acceptance': 'http://apis.development.quantillion.io',
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

    url = ENDPOINT_URL[endpoint]
    url = url.format(host=host, port=port, endpoint=endpoint)

    async_r = grequests.get(url, params=params, auth=AUTH)
    gevent.spawn(async_r.send).join()

    response = async_r.response

    if response is None:
        log.error('RESPONSE NONE %s %s', url, params)
        return []
    elif response.status_code == 200:
        log.debug(f' OK  {response.status_code}:{url}')
    elif response.status_code == 401:
        log.error(f' AUTH {response.status_code}:{url}')
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

    db_model = ENDPOINT_MODEL[endpoint]

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


def delete_duplicates(db_model):
    """
    Remove duplacates from table.
    """
    # make new session
    session = models.Session()
    log.debug('Count before %d', session.query(db_model).count())

    tablename = db_model.__table__.name
    session.execute(f"""
DELETE FROM {tablename} a USING (
     SELECT MIN(ctid) AS ctid, place_id, scraped_at
        FROM {tablename}
        GROUP BY (scraped_at, place_id) HAVING COUNT(*) > 1
 ) dups
 WHERE a.place_id = dups.place_id
 AND a.scraped_at = dups.scraped_at
 AND a.ctid <> dups.ctid
    """)
    session.commit()

    log.debug('Count after %d', session.query(db_model).count())


def get_previous_days():

    now = datetime.datetime.now()

    day = datetime.timedelta(days=1)

    today = now.date()
    tomorrow = (now + day).date()

    yield (str(today), str(tomorrow))

    # lets go 50 days in the past
    for i in range(1, settings.DAYS):
        past_time = now - i * day
        past_date1 = past_time.date()
        past_date2 = (past_time + day).date()
        yield (str(past_date1), str(past_date2))


def get_locations(work_id, endpoint, gen_dates, params={}):
    """
    Get google locations information with 'real-time' data
    """

    # generate past dates (global)
    for date1, date2 in gen_dates:
        # generate limit parameters

        params['startDate'] = date1
        params['endDate'] = date2

        do_limit_requests(work_id, endpoint, params)

    log.debug(f'Done {work_id}')


def do_limit_requests(work_id, endpoint, _gen_dates, params={}):
    """
    Do batch request of LIMIT each
    """

    params.update({'limit': LIMIT, 'skip': 0})

    while True:
        log.debug('%d %s', work_id, params)

        json_response = get_the_json(endpoint, params)
        add_locations_to_db(endpoint, json_response)

        if len(json_response) < LIMIT:
            # We are done with date
            break

        params['skip'] = params.get('skip', 0) + LIMIT

    log.debug(f'Done {params}')


def clear_current_table(endpoint):
    """
    Current data only contains latest and greatest
    """
    # make new session
    session = models.Session()
    db_model = ENDPOINT_MODEL[endpoint]
    session.query(db_model).delete()
    session.commit()


def run_workers(endpoint, workers=WORKERS, parralleltask=get_locations):
    """
    Run X workers processing search tasks
    """
    jobs = []

    # reset job status
    STATUS['done'] = False

    gen_dates = get_previous_days()

    if 'current' in endpoint:
        # get current data
        clear_current_table(endpoint)
        parralleltask = do_limit_requests
        workers = 1

    for i in range(workers):
        jobs.append(
            gevent.spawn(parralleltask, i, endpoint, gen_dates)
        )

    with gevent.Timeout(3600, False):
        # wait untill all tasks are done
        # but no longer than an hour
        gevent.joinall(jobs)

    for job in jobs:
        if not job.successful():
            raise job.exception

    delete_duplicates(ENDPOINT_MODEL[endpoint])



def main(args):

    endpoint = args.endpoint[0]
    engine = models.make_engine(section='docker')
    # models.Base.metadata.create_all(engine)
    models.set_engine(engine)

    if args.dedupe:
        delete_duplicates(ENDPOINT_MODEL[endpoint])
    else:
        # scrape the data!
        run_workers(endpoint)


if __name__ == '__main__':

    desc = "Scrape goolge quantillion api."
    inputparser = argparse.ArgumentParser(desc)
    inputparser.add_argument(
        'endpoint', type=str,
        default='realtime',
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1)

    inputparser.add_argument(
        '--dedupe',
        action='store_true',
        default=False,
        help="Remove duplicates")

    args = inputparser.parse_args()
    main(args)
