# Use Python Docker image created by Amsterdam
FROM amsterdam/docker_python:latest

# Create directory for data
RUN mkdir /data

# Copy requirements.txt to root
ADD /requirements.txt /requirements.txt

# Install all the required packages
RUN pip install -r /requirements.txt

# Copy all from current directory to /app directory in container
COPY . /app/

# Import data by downloading from objectstore and importing it into the database
# Script runs /app/download_from_objectstore.py and /app/load_data.py
ADD /run_import.sh /app/run_import.sh

# Do the .jenkins directory dance to enable data imports:
#COPY .jenkins/import /.jenkins-import/
#COPY .jenkins /app/.jenkins

# Run the import, which downloads data from object store
# and loads them into the database
WORKDIR /app/

CMD run_import.sh
