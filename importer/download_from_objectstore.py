"""
Access the druktemonitor project data on the data store.

For now the convention is that only relevant files are in the datastore and
the layout there matches the layout expected by our data loading scripts.

(We may have to complicate this in the future if we get to automatic
delivery of new data for this project.)
"""
import os
import logging
import configparser
import objectstore

from pathlib import Path
from swiftclient.client import Connection

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('swiftclient').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

config_auth = configparser.RawConfigParser()
config_auth.read('auth.conf')

config_src = configparser.RawConfigParser()
config_src.read('sources.conf')

# find object store password in environmental variables
OBJECTSTORE_PASSWORD = os.environ['STADSWERKEN_OBJECTSTORE_PASSWORD']

OS_CONNECT = {
    'auth_version': config_auth.get('extern_dataservices', 'ST_AUTH_VERSION'),
    'authurl': config_auth.get('extern_dataservices', 'OS_AUTH_URL'),
    'tenant_name': config_auth.get('extern_dataservices', 'OS_TENANT_NAME'),
    'user': config_auth.get('extern_dataservices', 'OS_USERNAME'),
    'os_options': {
        'tenant_id': config_auth.get(
            'extern_dataservices', 'OS_PROJECT_ID'),  # Project ID
        'region_name': config_auth.get('extern_dataservices', 'OS_REGION_NAME')
    },
    'key': OBJECTSTORE_PASSWORD
}


def file_exists(target):
    target = Path(target)
    return target.is_file()


def download_container(conn, container, targetdir):
    # list of container's content
    content = objectstore.get_full_container_list(conn, container['name'])

    # loop over files
    for obj in content:
        # check if object type is not application or dir, or a "part" file
        if obj['content_type'] == 'application/directory':
            logger.debug('skipping dir')
            continue

        if 'part' in obj['name']:
            logger.debug('skipping part')
            continue

        # target filename of object
        target_filename = os.path.join(targetdir, obj['name'])

        if file_exists(target_filename):
            logger.debug('skipping %s, file already exists', target_filename)
            continue

        # write object in target file
        with open(target_filename, 'wb') as new_file:
            _, obj_content = conn.get_object(container['name'], obj['name'])
            new_file.write(obj_content)


def download_containers(conn, datasets, targetdir):
    """
    Download the citydynamics datasets from object store.

    Simplifying assumptions:
    * layout on data store matches intended layout of local data directory
    * datasets do not contain nested directories
    * assumes we are running in a clean container (i.e. local data dir)
    * do not overwrite / delete old data
    """
    if not os.path.exists(targetdir):
        raise Exception('Local data directory does not exist.')

    resp_headers, containers = conn.get_account()

    logger.debug('Downloading containers ...')

    for c in containers:
        if c['name'] in datasets:
            logger.debug(c['name'])
            download_container(conn, c, targetdir)
