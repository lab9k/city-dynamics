#!/usr/bin/env bash

set -x
set -u
set -e

python scrape_api/models.py
python main_ETL.py /data
