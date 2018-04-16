#!/usr/bin/env bash

set -u
set -e

echo 0.0.0.0:5432:citydynamics:citydynamics:insecure > ~/.pgpass

chmod 600 ~/.pgpass

# dump occupation data
pg_dump  -t google_raw_locations* \
	 -Fc \
	 -U citydynamics \
	 -h 0.0.0.0 -p 5432 \
	 # -f google_raw.dump \
	 -f /tmp/backups/google_raw.dump \
	 citydynamics
