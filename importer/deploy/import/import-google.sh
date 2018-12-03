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

# Migrate temporary database, and drop specific tables.
dc run --rm importer python scrape_api/models.py --drop

# Import Quantillion data.
dc run --rm importer python scrape_api/slurp_api.py qa_realtime
dc run --rm importer python scrape_api/slurp_api.py qa_expected
dc run --rm importer python scrape_api/slurp_api.py qa_realtime/current
dc run --rm importer python scrape_api/slurp_api.py qa_expected/current

# Create a dump of the quantillion data.
# This dump will later be restored to the persistent database (see Jenkins subtask @ get_quantillion_expected_[ENV]).
dc exec -T database ./backup-db-google.sh

# All done. Remove used containers.
dc stop
dc rm --force
dc down
