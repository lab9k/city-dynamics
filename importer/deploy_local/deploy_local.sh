#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

docker-compose build database
docker-compose up -d database

docker-compose build importer
docker-compose run --rm importer

docker-compose run --rm api python manage.py migrate

docker-compose build analyzer
docker-compose run --rm analyzer