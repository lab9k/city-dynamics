#!/usr/bin/env bash

set -e
set -u
set -x

dc() {
    docker-compose $*
}

dc stop database
dc rm -f database
dc up -d database

# Wait until database container runs.
dc run --rm importer bash /app/deploy/docker-wait.sh

# Migrate the database.
dc run --rm api python manage.py migrate

# Restore Alpha database.
dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/quantillion_dump/google_raw_feb.dump

# Process data files, and write results to new tables in database.
dc run --rm importer python /app/main.py /data

# Create new tables in database.
dc run --rm importer python /app/scrape_api/models.py
