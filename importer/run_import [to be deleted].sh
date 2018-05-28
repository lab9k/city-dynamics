#!/usr/bin/env bash

# This script calls two python functions:
#
# scrape_api/models.py  <-- Creates models for all realtime API sources.
# main_ETL.py /data     <-- Fills the database (in Docker container) with data from the objectstore.

set -x
set -u
set -e

# Wait until database is running
bash deploy/docker-wait.sh

# TODO: MAKE THE MIGRATE STEP WORK HERE FOR LOCAL DEVELOPMENT!!
echo $PATH
docker-compose -f docker-compose.yml run --rm api python manage.py migrate


#######################################################
# THE ACTUAL HOTFIX. Should be commented out when Quantillion dump is correct.
pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --no-password --if-exists --clean data/google_raw_feb.dump

# Restore alpha_latest instead of fallback (google_raw_feb) when the Quantillion scraper works correctly.
#pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --no-password --if-exists --clean data/alpha_latest.dump
#######################################################

# Run importer code and migrate database
python scrape_api/models.py
python main_ETL.py /data

