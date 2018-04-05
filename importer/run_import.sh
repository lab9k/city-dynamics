#!/usr/bin/env bash

# This script calls two python functions:
#
# scrape_api/models.py  <-- Creates models for all realtime API sources.
# main_ETL.py /data     <-- Fills the database (in Docker container) with data from the objectstore.

set -x
set -u
set -e

python scrape_api/models.py
python main_ETL.py /data
