#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:citydynamics:citydynamics:insecure > ~/.pgpass

chmod 600 ~/.pgpass

# dump occupation data
pg_dump -t RealtimeAnalyzer \
	 -Fc \
	 -U citydynamics \
	 -h 0.0.0.0 -p 5432 \
	 -f /tmp/backups/own_realtime.dump \
	 citydynamics
