#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p cityd${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc down; dc kill ; dc rm -f -v' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc stop
dc rm
dc down
dc pull
dc build

dc up -d database
dc run --rm importer bash /app/deploy/docker-wait.sh
dc run --rm importer bash /app/run_import.sh
dc run --rm api python manage.py migrate

dc run --rm analyzer

dc exec -T database backup-db.sh citydynamics

dc stop
dc rm
dc down
