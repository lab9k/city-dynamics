#!/bin/sh

set -e
set -u
set -x


DIR="$(dirname $0)"

dc() {
	docker-compose -p citydgoogle${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc down; dc kill ; dc rm -f -v' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc stop
#dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm importer /app/deploy/docker-wait.sh

dc run --rm importer python scrape_api/models.py --drop

dc run --rm importer python scrape_api/slurp_api.py qa_realtime
dc run --rm importer python scrape_api/slurp_api.py qa_expected
dc run --rm importer python scrape_api/slurp_api.py qa_realtime/current
dc run --rm importer python scrape_api/slurp_api.py qa_expected/current

dc exec -T database ./backup-db-google.sh

# Create a dump of quantillion database in objectstore @ directory "quantillion_dump".
dc run --rm importer python -m objectstore.databasedumps /backups/google_raw.dump quantillion_dump --upload-db

# python -m objectstore.databasedumps . quantillion_dump --download-db
dc stop
##dc rm --force
dc down
