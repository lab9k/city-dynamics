#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p cityd_api_test -f ${DIR}/docker-compose.yml $*
}

trap 'dc down; dc kill ; dc rm -f -v' EXIT

dc stop
dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm tests

dc stop
dc rm --force
dc down
