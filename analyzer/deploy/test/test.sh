#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p cityd_analyze_test -f ${DIR}/docker-compose.yml $*
}


dc stop
dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm analyzer /app/deploy/docker-wait.sh
dc run --rm analyzer pytest


dc stop
dc rm --force
dc down
