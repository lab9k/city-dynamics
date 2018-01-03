# Use Python Docker image created by Amsterdam
FROM amsterdam/python

# Copy requirements.txt to root
ADD /requirements.txt /requirements.txt

# Install all the required packages
RUN pip install -r /requirements.txt

# Copy all from current directory to /app directory in container
COPY . /app/

ADD /run_index.sh /app/run_index.sh

WORKDIR /app/

CMD ./run_index.sh
