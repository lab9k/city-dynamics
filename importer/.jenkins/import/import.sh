#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p cityd -f ${DIR}/docker-compose.yml $*
}

# trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc rm
dc down
dc pull
dc build

dc up -d database

dc run --rm importer

dc run --rm analyzer

dc exec -T database backup-db.sh citydynamics
