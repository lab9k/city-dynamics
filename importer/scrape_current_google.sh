#!/usr/bin/env bash

set -x
set -u
set -e

cd scrape_api

# completely reset database
python models.py --drop

# load data in database
python slurp_api.py realtime/current
python slurp_api.py expected/current
