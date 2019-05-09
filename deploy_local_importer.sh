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

### Comment out one of the sections between double hashtags. Top one: downloading and parsing data.
### Bottom one: restore importer dump.
# Migrate the database.
# dc run --rm api python manage.py migrate

# Download the data
# dc run --rm importer python /app/main.py /data --download

# Restore Alpha database.
# dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/quantillion_dump/validated_dump_feb.dump

# Process data files, and write results to new tables in database.
# dc run --rm importer python /app/main.py /data
###
###

###
###
# Download the data
dc run importer python /app/main.py /data --download

# Restore importer dump
dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/dump_after_importer/20180626_dump_after_importer.dump
###
###

# Create new tables in database.
dc run --rm importer python /app/scrape_api/models.py
