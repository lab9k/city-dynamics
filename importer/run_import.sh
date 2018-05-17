#!/usr/bin/env bash

# This script calls two python functions:
#
# scrape_api/models.py  <-- Creates models for all realtime API sources.
# main_ETL.py /data     <-- Fills the database (in Docker container) with data from the objectstore.

set -x
set -u
set -e

python scrape_api/models.py
pg_restore --host=database --username=citydynamics --dbname=citydynamics data/google_raw_feb.dump
python main_ETL.py /data
