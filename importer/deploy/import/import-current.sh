#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p stadswerken_current -f ${DIR}/docker-compose.yml $*
}

# trap 'dc kill ; dc rm -f' EXIT

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

dc exec database ./backup-google-current.sh
