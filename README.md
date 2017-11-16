## City dynamics ##

Gaining and presenting insights regarding crowdedness in Amsterdam. How many people are where, at what moment?

Collaborators: Jerome Cremers, Rene Luijk, Swaan Dekkers

---

Create a local environment named `venv` and activate it. 
Exiting a virtual environment can be done using `deactivate`.

```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Install required packages.

```
pip install -r importer/requirements.txt
pip install -r web/requirements.txt
```

Create database

```
docker-compose build database
```

In a new window, run the database, and keep it running.

```
docker-compose up database
```

In order to connect to the object store, you need to store the password in an environment variable.

```
export EXTERN_DATASERVICES_PASSWORD="password"
```

Build the importer. This does not yet download any data from the objectstore.

```
docker-compose build importer
```

Download the data from the objectstore, store it in a folder `/data` within the container, and write it to the (locally running) database.

```
docker-compose up importer
```

The database is now filled with data and can be queried.

---

#Additional info for developers#

To add a new data source, make sure it is present in the root directory of the objectstore and configure `sources.conf`.
Create a parser function in parsers.py and make sure this function is called 'parser_x', where 'x' needs to be replaced with the name of the data source, stated between square brackets in `sources.conf`.