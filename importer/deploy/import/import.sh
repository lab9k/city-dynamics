#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
    docker-compose -p cityd${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

#trap 'dc down; dc kill ; dc rm -f -v' EXIT

# make sure we have anvironment variables
# and set them
export OBJECTSTORE_PASSWORD=$STADSWERKEN_OBJECTSTORE_PASSWORD
export OBJECTSTORE_USER=druktemeter

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups


# Start database container.
dc stop
dc rm --force
# dc down
dc pull
dc build
dc up -d database

# Wait until database container runs, and download data from objectstore.
dc run --rm importer bash /app/deploy/docker-wait.sh

### Comment out one of the sections between double hashtags. Top one: downloading and parsing data.
### Bottom one: restore importer dump.

# dc run --rm importer python /app/main.py /data --download

# # Migrate/Create target tables the database.
# dc run --rm api python manage.py migrate

# # Import Alpha database dump.
# #######################################################
# # THE ACTUAL HOTFIX. Should be commented out when Quantillion dump is correct.
# dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/quantillion_dump/validated_dump_feb.dump

# # Restore alpha_latest instead of fallback (validated_dump_feb.dump) when the Quantillion scraper works correctly.
# #dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/quantillion_dump/alpha_latest.dump
# #######################################################

# # Create new tables in database.
# dc run --rm importer python scrape_api/models.py

# # Process data files, and write results to new tables in database.
# dc run --rm importer python main.py /data

###
###

###
###
dc run --rm importer python /app/main.py /data --download

dc exec -T database pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean /data/dump_after_importer/20180626_dump_after_importer.dump

dc run --rm importer python scrape_api/models.py
###
###


# Run the analyzer.
dc run --rm analyzer

# Create a local database backup.
# dc exec -T database backup-db.sh citydynamics
dc exec -T database ./backup-analyzer.sh citydynamics

dc run --rm importer python -m objectstore.databasedumps /backups/analyzer.dump analyzer_dump --upload-db
dc run --rm importer python -m objectstore.databasedumps /backups/own_realtime.dump own_realtime_dump --upload-db 

# all ready. cleanup.
dc stop
dc rm --force
dc down
