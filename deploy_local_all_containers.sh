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

# Start database container.
docker-compose build database
docker-compose up -d database

# Restore Alpha database.
pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --if-exists --clean --no-password importer/data/quantillion_dump/google_raw_feb.dump

# Run importer container.
docker-compose build importer
docker-compose run --rm importer

# Run database table migrations.
docker-compose run --rm api python manage.py migrate

# Run analyzer container.
docker-compose build analyzer
docker-compose run --rm analyzer
