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

# Restore Quantillion dump to database
pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --no-password --clean data/google_raw_feb.dump

# Run importer code and migrate database
python scrape_api/models.py
python main_ETL.py /data
docker-compose run --rm api python manage.py migrate
