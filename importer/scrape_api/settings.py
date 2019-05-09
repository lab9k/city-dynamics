import os
import configparser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DAYS = int(os.getenv('GOOGLE_DAYS', 20))
LIMIT = 2000

AUTH_ROOT = os.path.abspath(os.path.join(BASE_DIR))
config_auth = configparser.RawConfigParser()
config_auth.read(AUTH_ROOT + '/auth.conf')

TESTING = {
    'running': False
}
