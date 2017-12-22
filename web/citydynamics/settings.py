# """
# Django settings for city-dynamics project.

# Generated by 'django-admin startproject' using Django 1.11.3.

# For more information on this file, see
# https://docs.djangoproject.com/en/1.11/topics/settings/

# For the full list of settings and their values, see
# https://docs.djangoproject.com/en/1.11/ref/settings/
# """


import os

from citydynamics.settings_databases import LocationKey,\
    get_docker_host,\
    get_database_key,\
    OVERRIDE_HOST_ENV_VAR,\
    OVERRIDE_PORT_ENV_VAR

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
insecure_secret = 'default_secret'
SECRET_KEY = os.getenv('SECRET_KEY', insecure_secret)
DEBUG = SECRET_KEY == insecure_secret

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'django.contrib.gis',
    'django_filters',
    'django_extensions',
    'datapunt_api',
    'citydynamics',
    'citydynamics.api',

    'rest_framework',
    'rest_framework_gis',


]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',

]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'citydynamics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'citydynamics/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

# LEAFLET_CONFIG = {
#     # conf here
#     'DEFAULT_CENTER': (52.370216, 4.895168),
#     'DEFAULT_ZOOM': 12,
#     'MIN_ZOOM': 11,
#     'MAX_ZOOM': 24,
#     'SPATIAL_EXTENT': (4.72, 52.28, 5.08, 52.43),
#     'SUBDOMAINS': ['t1', 't2', 't3', 't4'],
#     'TILES': 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png',
#     'RESET_VIEW': True,
# }


WSGI_APPLICATION = 'citydynamics.wsgi.application'


DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'city-dynamics'),
        'USER': os.getenv('DATABASE_USER', 'city-dynamics'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'city-dynamics'),
        'USER': os.getenv('DATABASE_USER', 'city-dynamics'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5403'
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'city-dynamics'),
        'USER': os.getenv('DATABASE_USER', 'city-dynamics'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'nl-NL'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True  # TO override date notation

DATE_FORMAT = '%d %b %Y'

USE_TZ = False

REST_FRAMEWORK = dict(
    PAGE_SIZE=500,
    MAX_PAGINATE_BY=100,

    DEFAULT_AUTHENTICATION_CLASSES=[],
    DEFAULT_PERMISSION_CLASSES=[],

    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    # or allow read-only access for unauthenticated users.
    DEFAULT_PAGINATION_CLASS='rest_framework.pagination.LimitOffsetPagination',
    DEFAULT_FILTER_BACKENDS=(
        'rest_framework.filters.DjangoFilterBackend',
    ),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))

# STATICFILES_DIR = (os.path.join(BASE_DIR, 'static'),)

# Upload location
MEDIA_URL = '/blabla/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            # 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'format': '%(levelname)s - %(name)s - %(message)s',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
