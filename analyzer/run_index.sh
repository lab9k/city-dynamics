#!/usr/bin/env bash

set -x
set -u
set -e

# calculate crowdedness index
python main.py docker
python main_fallback.py docker
python hotspots_fallback.py docker