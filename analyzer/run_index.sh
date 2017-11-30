set -x
set -u
set -e

# calculate crowdedness index
python /app/calc_index.py docker