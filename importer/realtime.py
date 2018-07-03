############
# Realtime #
############

##############################################################################################################
# This script combines datasources to create a realtime global crowdedness-score for the city of Amsterdam.
#
# Realtime sources:
#
# - OV-Fiets
#     - http://fiets.openov.nl/locaties.json
#
# - NDW
#     - http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson
#
# - P&R
#     - https://drukteradar.amsterdam.nl/api/apiproxy?api=parking_garages&format=json
#
# - Weercijfer
#     - https://www.weeronline.nl/Europa/Nederland/Amsterdam/4058223
#
# - KNMI
#     - https://weerlive.nl/api/json-data-10min.php?key=demo&locatie=Amsterdam
#
#
# Old realtime source, NOT used for production anymore:
#
# - Alpha Realtime
#     - https://drukteradar.amsterdam.nl/api/realtime/
##############################################################################################################


##############################################################################################################
# Imports and settings
import urllib.request
import json
import datetime
import requests
import re
import logging
from bs4 import BeautifulSoup
import configparser
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# Set logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# load config file
config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')
##############################################################################################################


##############################################################################################################
# Helper functions

def clamp(val, range_min=0, range_max=1):
    return max(min(range_max, val), range_min)


def rescale(org_val, org_min, org_max, new_min, new_max):
    return (new_max - new_min) * (org_val - org_min) / (org_max - org_min) + new_min


def get_conn():
    """Create a connection to the database."""
    dbconfig = 'docker'
    postgres_url = URL(
        drivername='postgresql',
        username=config_auth.get(dbconfig, 'user'),
        password=config_auth.get(dbconfig, 'password'),
        host=config_auth.get(dbconfig, 'host'),
        port=config_auth.get(dbconfig, 'port'),
        database=config_auth.get(dbconfig, 'dbname')
    )
    conn = create_engine(postgres_url)
    return conn


def create_row_sql(scraped_at, ov_fiets_crowdedness_score, ndw_crowdedness_score, pr_crowdedness_score,
                   knmi_crowdedness_score, weercijfer, combined_crowdedness_score, alp_mean, alp_count, diff,
                   w_fiets, w_ndw, w_pr, w_knmi, w_weer):
    row_sql = f"""
INSERT INTO public.datasets_realtimeanalyzer(
    scraped_at,
    ov_fiets_crowdedness_score,
    ndw_crowdedness_score,
    pr_crowdedness_score,
    knmi_crowdedness_score,
    weercijfer,
    combined_crowdedness_score,
    alp_mean,
    alp_count,
    diff,
    w_fiets,
    w_ndw,
    w_pr,
    w_knmi,
    w_weer)
VALUES(
    '{scraped_at}',
    '{ov_fiets_crowdedness_score}',
    '{ndw_crowdedness_score}',
    '{pr_crowdedness_score}',
    '{knmi_crowdedness_score}',
    '{weercijfer}',
    '{combined_crowdedness_score}',
    '{alp_mean}',
    '{alp_count}',
    '{diff}',
    '{w_fiets}',
    '{w_ndw}',
    '{w_pr}',
    '{w_knmi}',
    '{w_weer}');
    """

    return row_sql
##############################################################################################################


##############################################################################################################
# OV Fiets

def ov_fiets():

    ov_fiets_url = "http://fiets.openov.nl/locaties.json"

    # Load OV-fiets data
    with urllib.request.urlopen(ov_fiets_url) as url:
        ov_fiets = json.loads(url.read().decode())
        ov_fiets = ov_fiets['locaties']

    # Filter on location Amsterdam
    ov_fiets_amsterdam = dict((x, ov_fiets[x]) for x in ov_fiets if 'Amsterdam' in ov_fiets[x]['name'])

    # Count total amount of available rental bikes
    bike_count = sum([int(ov_fiets_amsterdam[x]['extra']['rentalBikes']) for x in ov_fiets_amsterdam])

    # Define assumptions about OV fiets bike amounts
    assumed_rented = 0.15   # We typically assume 20% of bikes to be always rented out.
    assumed_broken = 0.005  # We typically assume 0.05% of bikes to be always broken (but shown "available").
    total_bikes = 1200      # Bike_count 2018-06-13 @ 1:00 was 898. @ 23:19: 986 bikes. @ 1:26: 1040 bikes.
    total_bikes *= (1 - assumed_rented)

    # Heuristic: OV Fiets realtime crowdedness score. Range: [0-1]
    ov_fiets_crowdedness_score = (total_bikes - bike_count) / (total_bikes - (total_bikes * assumed_broken))
    ov_fiets_crowdedness_score = clamp(ov_fiets_crowdedness_score)

    # [DEBUG] Print bike count per station
    for k, v in ov_fiets_amsterdam.items():
        log.debug(f"[OV-Fiets] Station code: {k} \t # bikes: {v['extra']['rentalBikes']}")

    # [DEBUG] Print general bike counts
    log.debug(f"[OV-Fiets] bike_count: {bike_count}")
    log.debug(f"[OV-Fiets] ov_fiets_crowdedness_score: {ov_fiets_crowdedness_score}")

    return ov_fiets_crowdedness_score
##############################################################################################################


##############################################################################################################
# NDW

def ndw():

    ndw_url = "http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson"

    # Load NDW realtime data
    with urllib.request.urlopen(ndw_url) as url:
        ndw = json.loads(url.read().decode())
        ndw = ndw['features']

    # Filter on availability of velocity
    ndw_velocity = [(x['properties']['Type'], x['properties']['Velocity']) for x in ndw if
                    'Velocity' in x['properties'].keys()]

    # Compute average speeds for each road type
    H_sum = 0
    H_count = 0
    O_sum = 0
    O_count = 0

    for road_type, velocity in ndw_velocity:
        if road_type == "H":
            H_sum += velocity
            H_count += 1
        if road_type == "O":
            O_sum += velocity
            O_count += 1

    H_mean = H_sum / H_count
    O_mean = O_sum / O_count

    # Compute speed differences based on road type
    min_perc = 0.4  # assumed minimum speed (percentage of avg)
    # H_max = 101     # average 1:00 in the night of 2018-06-13 was 101.03 km/h.
    # H_min = H_max * min_perc
    O_max = 42      # average 1:00 in the night of 2018-06-13 was 41.68 km/h.
    O_min = O_max * min_perc

    # Only use "O" type roads for crowdedness computation.
    d_rescaled = rescale(O_mean, O_min, O_max, 0, 1)
    ndw_crowdedness_score = 1 - clamp(d_rescaled)

    # [DEBUG] Log statistics info
    log.debug(f"[NDW] H_mean: {H_mean}")
    log.debug(f"[NDW] O_mean: {O_mean}")
    log.debug(f"[NDW] ndw_crowdedness_score: {ndw_crowdedness_score}")

    return ndw_crowdedness_score
##############################################################################################################


##############################################################################################################
# P+R

def pr():

    pr_url = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json"

    # Load json
    pr = requests.get(pr_url).json()
    pr = pr['features']

    # Filter on 'State' = 'ok'
    pr = [x['properties'] for x in pr if x['properties']['State'] == 'ok']

    # Compute diff in short capacity (seems to be for short time visitors)
    # diff = sum([int(x['ShortCapacity']) - int(x['FreeSpaceShort']) for x in pr])

    # Compute total short capacity
    total_capacity = sum([int(x['ShortCapacity']) for x in pr])

    # Compute total free spaces
    total_free = sum([int(x['FreeSpaceShort']) for x in pr])

    # Heuristic: P+R crowdedness score. Range: [0-1]
    assumed_default_filling = 0.1  # Assume 10% of short stay parking spots is always filled.
    pr_crowdedness_score = 1 - ((total_free + total_free * assumed_default_filling) / total_capacity)
    pr_crowdedness_score = clamp(pr_crowdedness_score)

    # [DEBUG] Log statistics info
    log.debug(f"[P+R] total_capacity: {total_capacity}")
    log.debug(f"[P+R] total_free: {total_free}")
    log.debug(f"[P+R] pr_crowdedness_score: {pr_crowdedness_score}")

    return pr_crowdedness_score
##############################################################################################################


##############################################################################################################
# Weercijfer

def weer():

    # Get raw website data
    weeronline_url = "https://www.weeronline.nl/Europa/Nederland/Amsterdam/4058223"
    headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"}
    cookies = {'cookieConsent': 'true'}
    r = requests.get(weeronline_url, headers=headers, cookies=cookies)

    # Parse with BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get weercijfer from 5-day view
    res = soup.find('div', re.compile('wol-forecast-five-days-module__forecastDaysContainer.*'))
    weercijfer = int(list(res.ul.children)[1].find_all('div')[-1].text) / 10

    # [DEBUG] Print result
    log.debug(f"[WEER] weercijfer: {weercijfer}")

    return weercijfer
##############################################################################################################


##############################################################################################################
# KNMI

def knmi():

    # Documentatie URL: http://weerlive.nl/delen.php
    knmi_url = "https://weerlive.nl/api/json-data-10min.php?key=demo&locatie=Amsterdam"

    # Load NDW realtime data
    with urllib.request.urlopen(knmi_url) as url:
        knmi = json.loads(url.read().decode())
        knmi = knmi['liveweer'][0]

    # Heuristic: compute own KNMI "weercijfer" score. Range: [0-1]
    weer_scores = {
        "onbewolkt": 100,
        "licht bewolkt": 70,
        "half bewolkt": 50,
        "geheel bewolkt": 35,
        "mist": 35,  # Deze waarde wordt niet vernoemd in de documentatie, maar komt wel voor!
        "droog na regen": 35,
        "droog na motregen": 35,
        "zwaar bewolkt": 35,
        "lichte motregen": 30,
        "motregen": 25,
        "af en toe lichte regen": 25,
        "lichte regen": 20,
        "dichte motregen": 20,
        "lichte motregen en regen": 15,
        "motregen en regen": 15,
        "regen": 0}

    # Get score for current weather
    knmi_crowdedness_score = weer_scores[knmi['samenv'].lower()] / 100

    # [DEBUG] Print result
    log.debug(f"[KNMI] knmi_crowdedness_score: {knmi_crowdedness_score}")
    log.debug(f"[KNMI] Weer: {knmi['samenv']}")

    return knmi_crowdedness_score
##############################################################################################################


##############################################################################################################
# Alpha realtime score (only used for validation)

def alp():

    # Get Alpha data
    alp_url = "https://drukteradar.amsterdam.nl/api/realtime_quantillion/"
    alp = requests.get(alp_url, auth=('pipo', 'pluto')).json()
    alp = alp['results']

    # Compute mean Alpha realtime value
    alp_sum = 0
    alp_count = 0

    for x in alp:
        val = x['data']['Real-time']
        if val > 0:
            alp_sum += val
            alp_count += 1

    alp_mean = alp_sum / alp_count

    # [DEBUG] Print statistics
    log.debug(f"[ALP] Using {alp_count} locations for Alpha realtime score.")
    log.debug(f"[ALP] Alpha realtime score: {alp_mean} ({alp_count} locations)")

    # [DEBUG] Show currently used Alpha Realtime locations
    res = [dict(name=x['data']['name'], realtime=x['data']['Real-time'], expected=x['data']['Expected']) for x
           in alp if x['data']['Real-time'] > 0]
    for x in res:
        log.debug(f"[ALP] str(x)")

    return alp_mean, alp_count
##############################################################################################################


##############################################################################################################
# Main routine

def main():
    '''Compute crowdedness score by combining multiple realtime datasources.'''

    # Get crowdedness scores for all sources.
    success = False
    attempts = 0
    while success is False and attempts < 100:
        try:
            ov_fiets_crowdedness_score = ov_fiets()
            log.info(f"ov_fiets_crowdedness_score: {ov_fiets_crowdedness_score}")
            ndw_crowdedness_score = ndw()
            log.info(f"ndw_crowdedness_score: {ndw_crowdedness_score}")
            pr_crowdedness_score = pr()
            log.info(f"pr_crowdedness_score: {pr_crowdedness_score}")
            knmi_crowdedness_score = knmi()
            log.info(f"knmi_crowdedness_score: {knmi_crowdedness_score}")
            weercijfer = weer()
            log.info(f"weercijfer: {weercijfer}")
            success = True
        except Exception:
            attempts += 1

    # If no scores have been gathered after all attempts, exit script.
    if success is False:
        log.info("Could not gather data to compute crowdedness score. Exiting.")
        exit()

    # Define weights for each source.
    w_fiets = 10
    w_ndw = 35
    w_pr = 25
    w_knmi = 15
    w_weer = 15

    # Turn KNMI and weercijfer weights down at night.
    # Retained percentage of weight (@ each hour): 90@1h 65@2h, 40@3h, 15@4h, 40@5h, 65@6h, 90@7h
    hour = datetime.datetime.now().hour
    if hour > 0 and hour < 8:
        offset = abs(4 - hour) + 0.6
        factor = .25 * offset
        w_knmi *= factor
        w_weer *= factor

    # Compute combined crowdedness sccore.
    combined_crowdedness_score = ((w_fiets * ov_fiets_crowdedness_score +
                                   w_ndw * ndw_crowdedness_score +
                                   w_pr * pr_crowdedness_score +
                                   w_knmi * knmi_crowdedness_score +
                                   w_weer * weercijfer)
                                  / (w_fiets + w_ndw + w_pr + w_knmi + w_weer))

    # Show resulting crowdedness value
    log.info(f"combined_crowdedness_score: {combined_crowdedness_score}")

    # Try to get score from Alpha source, and compare with own score for validation.
    alp_mean = 0
    alp_count = 0
    diff = 0
    try:
        alp_mean, alp_count = alp()
        log.info(f"alp_mean: {alp_mean} ({alp_count} locations)")
        diff = combined_crowdedness_score - alp_mean
        log.info(f"Difference (own - alp):  {diff}")
    except Exception:
        log.info("No alpha value present. Leaving the difference as 0.")
        pass

    # write to db
    conn = get_conn()
    scraped_at = datetime.datetime.now()
    row_sql = create_row_sql(scraped_at,
                             ov_fiets_crowdedness_score,
                             ndw_crowdedness_score,
                             pr_crowdedness_score,
                             knmi_crowdedness_score,
                             weercijfer,
                             combined_crowdedness_score,
                             alp_mean,
                             alp_count,
                             diff,
                             w_fiets,
                             w_ndw,
                             w_pr,
                             w_knmi,
                             w_weer)
    conn.execute(row_sql)

##############################################################################################################


##############################################################################################################
if __name__ == "__main__":
    main()
##############################################################################################################
