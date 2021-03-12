"""
Django settings for appstore project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from pathlib import Path

NESTED_SETTINGS_DIR = Path(__file__).parent.resolve(strict=True)
APPSTORE_DIR = NESTED_SETTINGS_DIR.parent
BASE_DIR = APPSTORE_DIR.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', "")) # Empty quotes equates to false in kubernetes env.
DEV_PHASE = os.environ.get('DEV_PHASE', 'local')  # stub, local, dev, val, prod.
TYCHO_MODE = os.environ.get('TYCHO_MODE', 'null' if DEV_PHASE == 'stub' else 'live')

# DJANGO and SAML login toggle flags, lower cased for ease of comparison
ALLOW_DJANGO_LOGIN = os.environ.get('ALLOW_DJANGO_LOGIN',
                                    "True" if DEV_PHASE == "local" or DEV_PHASE == 'stub' else "False").lower()
ALLOW_SAML_LOGIN = os.environ.get('ALLOW_SAML_LOGIN', "True").lower()

IMAGE_DOWNLOAD_URL = os.environ.get('IMAGE_DOWNLOAD_URL', 'https://braini-metalnx.renci.org/metalnx')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ["*", "127.0.0.1", "0.0.0.0"] # localhost/0.0.0.0 required when DEBUG=false]

APPEND_SLASH = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'core',
    'middleware',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'bootstrapform',
    'corsheaders',
    'rest_framework',
    'api',
    'spa',
    'debug_toolbar',
]

SITE_ID = 4

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

if DEBUG=="True" and DEV_PHASE in ("local", "stub", "dev"):
    MIDDLEWARE += [
        'corsheaders.middleware.CorsMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
]

#
# After a user logs in we also check to see if they are part of an
# authorized user/whitelist. We need to perform this check regardless of if
# data is being routed through the existing Django template frontend found in
# `core`, or through the Django Rest Framework endpoints that can be used by
# the new react frontend, or other api consuming tools.
#
# Rather than toggling the rest_framework endpoints and frontend app on/off
# we can make sure that there is always a middleware present that checks if the
# user is an authorized user (table: core_authorizeduser) with the main difference
# being if the middleware raises a redirect for an unauthorized user, or if
# the middleware raises a 403 for the consuming application to handle. See
# `middleware/filter_whitelist_middleware.py` and `middleware/authorized_user.py`
# for additional details.
#
WHITELIST_REDIRECT = os.environ.get('WHITELIST_REDIRECT', 'true').lower()
if WHITELIST_REDIRECT == "true":
    MIDDLEWARE.append('middleware.filter_whitelist_middleware.AllowWhiteListedUserOnly')
else:
    MIDDLEWARE.append('middleware.authorized_user.AuthorizedUserCheck')

# Add any additional middleware that's not conditional
MIDDLEWARE += [
    'middleware.session_idle_timeout.SessionIdleTimeout',
]

if DEBUG=="True" and DEV_PHASE in ("local", "stub", "dev"):
    CORS_ALLOWED_ORIGINS = [
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

# Debug toolbar setting
INTERNAL_IPS = [
    '127.0.0.1',
]

# Session Timeout Configuration
SESSION_IDLE_TIMEOUT = 300

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'appstore@renci.org')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get("APPSTORE_DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
DEFAULT_SUPPORT_EMAIL = os.environ.get("APPSTORE_DEFAULT_SUPPORT_EMAIL", EMAIL_HOST_USER)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 3
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400  # 1 day in seconds
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

ACCOUNT_FORMS = {'signup': 'appstore.forms.CustomSignupForm'}

SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get('ACCOUNT_DEFAULT_HTTP_PROTOCOL', "http")

SOCIALACCOUNT_PROVIDERS = \
    {'google':
         {'SCOPE': ['profile', 'email'],
          'AUTH_PARAMS': {'access_type': 'offline'}}}

SOCIALACCOUNT_STORE_TOKENS = True

ROOT_URLCONF = 'appstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [str(BASE_DIR / "templates")],
        'OPTIONS': {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                'django.contrib.messages.context_processors.messages',
                'appstore.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'appstore.wsgi.application'


DB_DIR = Path(os.environ.get('OAUTH_DB_DIR', BASE_DIR))
DB_FILE = Path(os.environ.get('OAUTH_DB_FILE', 'DATABASE.sqlite3'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / DB_FILE,
    }
}

IRODS_COLLECTION = os.environ.get('IROD_COLLECTIONS', "")
IRODS_ZONE = os.environ.get('IROD_ZONE', "")
##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
# local_settings = __import__(local_settings_module, globals(), locals(), ['*'])
# for k in dir(local_settings):
#    locals()[k] = getattr(local_settings, k)

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'


# PIVOT HAIL APP specific settings
INITIAL_COST_CPU = 6
INITIAL_COST_MEM = 6  # in MB

# phenotype specific settings
PHENOTYPE_REDIRECT_URL = "https://monarchinitiative.org/analyze/phenotypes"

OIDC_SESSION_MANAGEMENT_ENABLE = True
SITE_URL = 'http://localhost:8000'

LOGIN_REDIRECT_URL = '/apps/'
LOGIN_URL = '/accounts/login'
ADMIN_URL = '/admin'
LOGIN_WHITELIST_URL = '/login_whitelist/'

SAML_URL = '/accounts/saml'
SAML_ACS_URL = '/saml2_auth/acs/'

APP_CONTEXT_URL = "/api/v1/context"
APP_LOGIN_PROVIDER_URL = "/api/v1/providers"

min_django_level = 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # keep Django's default loggers
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'timestampthread': {
            'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-25.25s  ]  %(message)s",
        },
    },
    'handlers': {
        'syslog': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/system_warnings.log',
            'formatter': 'timestampthread',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
        'djangoLog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/django_debug.log',
            'formatter': 'timestampthread',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
        'app_store_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/app_store.log',
            'formatter': 'timestampthread',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {

        '': {
            'handlers': ['app_store_log', 'console'],
            'propagate': False,
            'level': 'DEBUG'
            # 'level': 'INFO',
        },
        'django': {
            'handlers': ['syslog', 'djangoLog', 'console'],
            'level': min_django_level,
            'propagate': False,

        },
        # https://docs.djangoproject.com/en/1.11/topics/logging/#django-template
        'django.template': {
            'handlers': ['syslog', 'djangoLog'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['syslog'],
            'level': 'WARNING',
            'propagate': False,
        },
        'admin': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'tycho.client': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'tycho.kube': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
