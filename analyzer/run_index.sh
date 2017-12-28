#!/usr/bin/env bash

set -x
set -u
set -e

# calculate crowdedness index
python calc_index.py docker
