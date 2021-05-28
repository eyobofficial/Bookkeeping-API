import os
from datetime import timedelta
from decouple import config, Csv
from environ import Path


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__) - 3


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]


# Third Party apps
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'phonenumber_field',
    'storages',
    'dj_rest_auth',
    'drf_yasg',
    'django_countries',
]


# Project apps
INSTALLED_APPS += [
    'accounts.apps.AccountsConfig',
    'shared.apps.SharedConfig',
    'business.apps.BusinessConfig',
    'customers.apps.CustomersConfig',
    'expenses.apps.ExpensesConfig',
    'inventory.apps.InventoryConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'config.wsgi.application'


#  POSTRESQL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('RDS_DB_NAME'),
        'USER': config('RDS_USERNAME'),
        'PASSWORD': config('RDS_PASSWORD'),
        'HOST': config('RDS_HOSTNAME'),
        'PORT': config('RDS_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Authentications
AUTHENTICATION_BACKENDS = [
    'accounts.backends.phonebackend.PhoneNumberBackend',
    'accounts.backends.emailbackend.EmailBackend',
]


# Custom Auth User Model
AUTH_USER_MODEL = 'accounts.CustomUser'


# Cors Headers
CORS_ORIGIN_ALLOW_ALL = True


# Default Admin Account
DEFAULT_ADMIN_EMAIL = config('ADMIN_EMAIL')
DEFAULT_ADMIN_PHONE_NUMBER = config('ADMIN_PHONE_NUMBER')
DEFAULT_ADMIN_PASSWORD = config('ADMIN_PASSWORD')
DEFAULT_ADMIN_FIRST_NAME = config('ADMIN_FIRST_NAME', 'Admin')
DEFAULT_ADMIN_LAST_NAME = config('ADMIN_LAST_NAME', 'User')


# Project Name
PROJECT_NAME = 'Dukka API'


# Django Phonenumber Field
PHONENUMBER_DEFAULT_REGION = 'ET'
PHONENUMBER_DB_FORMAT = 'NATIONAL'


# Start-up fixtures
FIXTURES = ['business_types']


# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Site ID
SITE_ID = 1


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'dukka-auth'
JWT_AUTH_REFRESH_COOKIE = 'dukka-refresh-token'
JWT_AUTH_RETURN_EXPIRATION = True


# All Auth
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'phone_number'


# Simple JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=200),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# Africa's Talking

AFRICASTALKING_USERNAME = config('AFRICASTALKING_USERNAME')
AFRICASTALKING_API_KEY = config('AFRICASTALKING_API_KEY')
AFRICASTALKING_SENDER_ID = config('AFRICASTALKING_SENDER_ID')
