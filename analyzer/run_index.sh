#!/usr/bin/env bash

# This script kicks off the entire analyzer pipeline:
#
# The module main.py is called in order to compute a drukteindex value for each vollcode.
# The module hotspots_drukteindex.py is called in order to compute a drukteindex value for each hotspot.
# In future versions, the functionality of hotspots_drukteindex.py is likely to get integrated in main.py.

set -x
set -u
set -e

# Calculate crowdedness index
python main.py docker
#python main_fallback.py docker
python hotspots_drukteindex.py
