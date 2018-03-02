#!/usr/bin/env bash

set -x
set -u
set -e

# download data from the object store
python download_from_objectstore.py /data

# Import dump of Alpha data table (originally served by Quantillion API)
pg_restore --host=database --port=5432 --username=citydynamics --dbname=citydynamics --no-password --clean data/google_raw.dump

# TODO: Make use of pgpass.conf password file instead of exporting a PGPASSWORD environment variable.
# TODO: For some reason, the password file is not used or correctly interpreted atm since no db connection can be made.
# export PGPASSFILE=./pgpass.conf
# cat $PGPASSFILE
# pg_restore --dbname=citydynamics data/google_raw.dump

# Modify new Alpha data table
python modify_alpha_table.py docker

# load data in database
python load_data.py /data docker

# add geometry
python add_areas.py docker

# create empty tables
python sql_migrations.py docker