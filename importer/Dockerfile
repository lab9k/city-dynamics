# Use Python Docker image created by Amsterdam
FROM amsterdam/python

# Create directory for data
RUN mkdir /data

# Copy requirements.txt to root
ADD /requirements.txt /requirements.txt

# Install all the required packages
RUN pip install -r /requirements.txt

# Copy all from current directory to /app directory in container
COPY . /app/

COPY ./deploy /deploy/

WORKDIR /app/
