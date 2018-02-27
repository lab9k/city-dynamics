#!/usr/bin/env bash

set -x
set -u
set -e

# download data from the object store
python download_from_objectstore.py /data

# Import dump of Alpha data table (originally served by Quantillion API)
pg_restore -h database -p 5432 -U citydynamics -d citydynamics google_raw.dump

# Modify new Alpha data table
python modify_alpha_table.py

# load data in database
python load_data.py /data docker

# add geometry
python add_areas.py docker

# create empty tables
python sql_migrations.py docker