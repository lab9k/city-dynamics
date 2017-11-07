set -x
set -u
set -e

# download data from the object store
python /app/download_from_objectstore.py /data

# load data in database
python /app/load_data.py /data docker

# add geometry
python /app/run_additional_sql.py docker