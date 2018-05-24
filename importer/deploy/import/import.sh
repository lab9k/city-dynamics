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
dc rm --force
dc down
# dc pull
dc build

dc up -d database

# Download dump of quantillion database in objectstore @ directory "quantillion_dump".
# dc run --rm importer python -m objectstore.databasedumps /data/ quantillion_dump --download-db

dc run --rm importer bash /app/deploy/docker-wait.sh
dc run --rm importer python /app/main_ETL.py /data --download


#######################################################
# THE ACTUAL HOTFIX. Should be commented out when Quantillion dump is correct.
dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/google_raw_feb.dump

# Restore alpha_latest instead of fallback (google_raw_feb) when the Quantillion scraper works correctly.
#dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/alpha_latest.dump
#######################################################

dc run --rm importer bash /app/run_import.sh
dc run --rm api python manage.py migrate
dc run --rm analyzer
dc exec -T database backup-db.sh citydynamics

dc stop
dc rm --force
dc down
