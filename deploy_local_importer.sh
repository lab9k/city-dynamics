#!/usr/bin/env bash

# Wait until database container runs, and download data from objectstore.
docker-compose run --rm importer bash /app/deploy/docker-wait.sh
docker-compose run --rm importer python /app/main_ETL.py /data --download

# Create new tables in database.
python scrape_api/models.py

# Process data files, and write results to new tables in database.
python main_ETL.py /data

# Migrate the database.
docker-compose run --rm api python manage.py migrate
