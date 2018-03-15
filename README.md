# City dynamics #

Gaining and presenting insights regarding crowdedness in Amsterdam. How many people are where, at what moment?

Collaborators: Jerome Cremers, Thomas Jongstra, Stephan Preeker, Swaan Dekkers

---

To keep this project's dependencies and libraries separate from your global Python instance, create a local virtual Python environment. For Anaconda users, see https://conda.io/docs/user-guide/tasks/manage-environments.html. For non-Anaconda users, see https://virtualenvwrapper.readthedocs.io/en/latest/.

Install required packages.

```
pip install -r importer/requirements.txt
pip install -r analyzer/requirements.txt
pip install -r api/requirements.txt
```

If you get errors in one of the steps above about the version of `setuptools` you should update it.

```
pip install setuptools --upgrade
```


Create database

```
docker-compose pull database
```

In a new window, run the database, and keep it running.

```
docker-compose up database
```

In order to connect to the object store, you need to store the password in an environment variable.

```
export STADSWERKEN_OBJECTSTORE_PASSWORD="password"
```

Build the importer. This does not yet download any data from the objectstore.

```
docker-compose build importer
```

Download the data from the objectstore, store it in a folder `/data` within the Importer container, and write it to the (locally running) database.

```
docker-compose run importer /app/run_import.sh
```

The database is now filled with data and can be queried.

---

To get the front end working, the **analyzer**, **api** and **front** containers should be built and activated in Docker. This can be done with the following commands:

```
docker-compose build analyzer
docker-compose build api
docker-compose build front
docker-compose up analyzer
docker-compose up api
docker-compose up front
```
---

The front end of the application can now be visualized locally by opening `front/index.html` in a browser.

## Additional info for developers ##

To add a new data source, make sure it is present in the root directory of the objectstore and configure `sources.conf`.
Create a parser function in `parsers.py` and call this function 'parser_x', where 'x' needs to be replaced with the name of the data source, stated between square brackets in `sources.conf`.

## RUN TESTS ##

To run the entire test test. run 
```
api/deploy/test/the_tests.sh
importer/deploy/test/tests.sh
```

The api test are run manualy in your local development environment by
```
python manage.py test --nomigrations
```

