#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p cityd${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

#trap 'dc down; dc kill ; dc rm -f -v' EXIT

# make sure we have anvironment variables
# and set them
export OBJECTSTORE_PASSWORD=$STADSWERKEN_OBJECTSTORE_PASSWORD
export OBJECTSTORE_USER=druktemeter

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups


# Start database container.
dc stop
dc rm --force
# dc down
dc pull
dc build
dc up -d database

# Wait until database container runs, and download data from objectstore.
dc run --rm importer bash /app/deploy/docker-wait.sh

# Download from objectstore (alleen bronnen met ENABLED=YES @ sources.conf)
dc run --rm importer python /app/main.py /data --download

# Restore bronnen die al met de importer verwerkt zijn (statische dumps)
dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/dump_after_importer/20180626_dump_after_importer.dump

# Perform database migration.
dc run --rm importer python scrape_api/models.py

# Run the analyzer.
dc run --rm analyzer

# Create a local database backup.
dc exec -T database ./backup-analyzer.sh citydynamics

# all ready. cleanup.
dc stop
dc rm --force
dc down
