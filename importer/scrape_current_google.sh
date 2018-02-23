#!/usr/bin/env bash

set -x
set -u
set -e

# download data from the object store
cd scrape_quantillion

python models.py

# load data in database
python slurp_api.py realtime/current
