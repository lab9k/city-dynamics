#!/usr/bin/env bash

set -u
set -e

echo 0.0.0.0:5432:citydynamics:citydynamics:insecure > ~/.pgpass

chmod 600 ~/.pgpass

# dump occupation data
pg_dump -t verblijversindex \
	 -t stadsdeel \
	 -t datasets_buurtcombinatiedrukteindex \
	 -t datasets_hotspotsdrukteindex \
	 -t buurtcombinatie \
	 -t hotspots \
	 -t drukte_index* \
     -t parkeren \
	 -t gvb \
	 -Fc \
	 -U citydynamics \
	 -h 0.0.0.0 -p 5432 \
	 -f /tmp/backups/analyzer.dump \
	 citydynamics
