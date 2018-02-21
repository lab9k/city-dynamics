Download google scraping data from quantillion.
=================================================

author: Stephan Preeker.

Instructions.
---------------

Network should allow for port 3001 to be open. (not the case withing the municipality of amsterdam)



set `ENVIRONMENT` to acceptance of production
set `QUANTILLION_PASSWORD` you can find it in rattic/password management

        docker-compose up database


# create database models, table names get postfix of 'acceptance' / 'production'

        pip install -r requirements.txt

        python models.py

# now you can run:

        python slurp_api.py

# Data is now stored in two tables, with a raw json field.

Tests
======

pytest
