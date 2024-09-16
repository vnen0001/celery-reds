"""
Django settings for azure_backend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv,find_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# env_path = BASE_DIR / 'azure_backend/cred.env'
# load_result = load_dotenv(env_path)
# print(f"Attempted to load .env file from: {env_path}")
# print(f"Load dotenv result: {load_result}")
load_dotenv('vital_voices_project/cred.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.environ.get('DJANGO_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True#os.environ.get('DJANGO_DEBUG')

ALLOWED_HOSTS = ['*']
if DEBUG ==True:
    ALLOWED_HOSTS=['localhost','127.0.0.1']
else:
    ALLOWED_HOSTS=['https://vitalvoices.live',"https://yellow-dune-0db69390f.5.azurestaticapps.net"]

def database_cred():
    
    print(f"Load dotenv result")  # Debug print
    creds = {
        'server': os.environ.get('DB_SERVER'),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USERNAME'),
        'password': os.environ.get('DB_PASSWORD'),
        'DEBUG':os.environ.get('DJANGO_DEBUG'),

    }
  # Debug print
    return creds
print(DEBUG)
print(database_cred())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vital_voices',
    'rest_framework',
    'corsheaders',
    'django_redis',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vital_voices_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vital_voices_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

credentials = database_cred()
if all(credentials.values()):
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': credentials['database'],
            'USER': credentials['user'],
            'PASSWORD': credentials['password'],
            'HOST': credentials['server'],
            'OPTIONS': {
                'driver': 'ODBC Driver 18 for SQL Server',
                'encrypt': 'yes',
                'trustServerCertificate': 'no'
            },
        }
    }
else:
    print("WARNING: Database credentials are not properly set in the environment variables.")
    print(credentials)
    print("Using sqlite3 as a fallback.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
     "http://127.0.0.1:3000",
     "http://localhost:5174",
     "http://localhost:5173",
     "https://20.55.67.148",
    "https://yellow-dune-0db69390f.5.azurestaticapps.net",
    "https://vitalvoices.live"
]
REDIS_HOST = os.environ.get('REDIS_SERVER')  # Replace with your VM's IP address
REDIS_PORT = os.environ.get("REDIS_PORT")

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


from django.db import connections
from django.db.utils import OperationalError
from redis import Redis

def test_connections():
    # Test database connection
    try:
        connections['default'].cursor()
        print("Database connection successful")
    except OperationalError:
        print("Database connection failed")

    # Test Redis connection
    try:
        r = Redis(host=REDIS_HOST, port=REDIS_PORT)
        r.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {str(e)}")

test_connections()

