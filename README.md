## City dynamics ##

City-dynamics

Collaborators: Jerome Cremers, Rene Luijk, Swaan Dekkers

---

Create database

```
docker-compose build database
```

Create a local environment named `venv` and activate. Exiting a virtual environment can be done using `deactivate`.

```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Install required packages.

```
pip install -r web/requirements.txt
```

In a new window, run the database, and keep it running.

```
docker-compose up database
```

Before you can login to the site, you must create the tables and an admin useraccount in the database:

```
python web/manage.py migrate
python web/manage.py createsuperuser
```

In order to connect to the object store, you need to store the password in an environment variable. In UNIX:

```
export EXTERN_DATASERVICES_PASSWORD="password"
```

Build importer. Does not yet download data from object store.

```
docker-compose build importer
```

Download the data from the object store to local folder `/data` within the container.

```
docker-compose up importer
```