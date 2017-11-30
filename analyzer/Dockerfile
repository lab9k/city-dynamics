# Use Python Docker image created by Amsterdam
FROM amsterdam/docker_python:latest

# Copy requirements.txt to root
ADD /requirements.txt /requirements.txt

# Install all the required packages
RUN pip install -r /requirements.txt

# Copy all from current directory to /app directory in container
COPY . /app/

# Import data by downloading from objectstore and importing it into the database
# Script runs /app/download_from_objectstore.py and /app/load_data.py
ADD /run_index.sh /app/run_index.sh

# Run the import, which downloads data from object store
# and loads them into the database
CMD /app/run_index.sh