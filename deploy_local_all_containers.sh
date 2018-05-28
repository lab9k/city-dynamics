#!/usr/bin/env bash

# This script does the following things:
#
# 1. Start docker containers to keep the service running (database, api)
# 2. Run importer docker once to import data
# 3. Run api docker once to migrate data
# 4. Run analyzer docker once to create predictions.
#    Done!

set -u   # crash on missing env variables
set -e   # stop on any error

docker-compose build database
docker-compose up -d database

docker-compose build importer
docker-compose run --rm importer

docker-compose run --rm api python manage.py migrate

docker-compose build analyzer
docker-compose run --rm analyzer
