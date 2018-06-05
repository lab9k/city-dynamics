#!/usr/bin/env bash

# Wait until database container runs.
docker-compose run --rm importer bash /app/deploy/docker-wait.sh

# Migrate the database.
docker-compose run --rm api python manage.py migrate

# Import datasets.
docker-compose run --rm importer python /app/main.py /data

# Restore Alpha database.
pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --if-exists --clean --no-password importer/data/quantillion_dump/google_raw_feb.dump

# Create new tables in database.
python ./importer/scrape_api/models.py

# Process data files, and write results to new tables in database.
python ./importer/main.py ./data
