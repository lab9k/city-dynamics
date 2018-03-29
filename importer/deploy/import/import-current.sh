#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p qa_current${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc stop
dc rm --force
dc down
dc pull
dc build
dc up -d database

dc run --rm importer /app/deploy/docker-wait.sh

dc run --rm importer ./scrape_current_google.sh

dc exec -T database ./backup-google-current.sh
