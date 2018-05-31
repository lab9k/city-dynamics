#!/usr/bin/env bash

# Wait until database container runs, and download data from objectstore.
docker-compose run --rm importer bash /app/deploy/docker-wait.sh
docker-compose run --rm importer python /app/main_ETL.py /data --download

# Restore Alpha database.
pg_restore --username=citydynamics --dbname=citydynamics --if-exists --clean --no-password /data/quantillion_dump/google_raw_feb.dump

# Create new tables in database.
python scrape_api/models.py

# Process data files, and write results to new tables in database.
python main.py /data

# Migrate the database.
docker-compose run --rm api python manage.py migrate

