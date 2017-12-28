#!/usr/bin/env bash

set -x
set -u
set -e

# download data from the object store
python download_from_objectstore.py /data

# load data in database
python load_data.py /data docker

# add geometry
python add_areas.py docker
