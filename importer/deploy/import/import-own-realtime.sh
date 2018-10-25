#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p own_realtime${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc down; dc kill ; dc rm -f -v' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc stop
dc rm --force
dc down
dc pull
dc build
dc up -d database

# Start temporary database.
dc run --rm importer /app/deploy/docker-wait.sh

# Migrate temporary database.
dc run --rm api python manage.py migrate

# Run realtime script to compute realtime value (and write to temporary database).
dc run --rm importer python ./realtime.py

# Backup realtime data to temporary file, so it can be imported into the running database server (on ACC and PROD).
dc exec -T database ./backup-own-realtime.sh

dc stop
dc rm --force
dc down
