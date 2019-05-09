#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p cityd${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

#trap 'dc down; dc kill ; dc rm -f -v' EXIT

# Make sure we have environment variables, and set them.
export OBJECTSTORE_PASSWORD=$STADSWERKEN_OBJECTSTORE_PASSWORD
export OBJECTSTORE_USER=druktemeter

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

# Make sure any possible old database instances (in this scope) are down.
dc stop
dc rm --force
dc down
dc pull
dc build

# Start database container.
dc up -d database

# Wait until database container is running.
dc run --rm importer /app/deploy/docker-wait.sh

# Download from objectstore (alleen bronnen met ENABLED=YES @ sources.conf)
dc run --rm importer python /app/main.py /data --download

# Restore bronnen die al met de importer verwerkt zijn (statische dumps)
dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/dump_after_importer/20180626_dump_after_importer.dump

# Run the analyzer.
dc run --rm analyzer

# Create a local database backup.
dc exec -T database ./backup-analyzer.sh citydynamics

# All done. Remove used containers.
dc stop
dc rm --force
dc down
