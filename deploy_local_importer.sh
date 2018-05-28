#!/usr/bin/env bash

docker-compose run --rm importer bash /app/deploy/docker-wait.sh
docker-compose run --rm importer python /app/main.py /data