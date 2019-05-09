#!/usr/bin/env bash

set -x
set -u
set -e

# Quantillion scraping
cd scrape_api

# completely reset database
python models.py --drop

# load data in database
python slurp_api.py qa_realtime/current
python slurp_api.py qa_expected/current
