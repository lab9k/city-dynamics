#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p citydgoogle -f ${DIR}/docker-compose.yml $*
}

# trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc stop
#dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm importer /app/deploy/docker-wait.sh

dc run --rm importer python scrape_quantillion/models.py --drop
dc run --rm importer python scrape_quantillion/slurp_api.py realtime
dc run --rm importer python scrape_quantillion/slurp_api.py expected
dc run --rm importer python scrape_quantillion/slurp_api.py realtime/current
dc run --rm importer python scrape_quantillion/slurp_api.py expected/current

# dc run --rm analyzer

dc exec -T database ./backup-db-google.sh
