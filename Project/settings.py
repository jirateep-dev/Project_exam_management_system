"""
Django settings for Project project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '66981n9uombkzs)ebdt_4cx@-0k_i&atg(h)cm30(=nj-sk34y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",)
# # AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",'django.contrib.auth.backends.ModelBackend',)

# # The URL of the LDAP server.
# LDAP_AUTH_URL = "ldap://161.246.38.141:389"

# # Initiate TLS on connection.
# LDAP_AUTH_USE_TLS = False

# # The LDAP search base for looking up users.
# # LDAP_AUTH_SEARCH_BASE = "ou=people,dc=example,dc=com"
# LDAP_AUTH_SEARCH_BASE = "ou=users"

# # The LDAP class that represents a user.
# LDAP_AUTH_OBJECT_CLASS = "inetOrgPerson"

# # User model fields mapped to the LDAP
# # attributes that represent them.
# LDAP_AUTH_USER_FIELDS = {
#     "username": "sAMAccountName",
#     "first_name": "givenName",
#     "last_name": "sn",
#     "email": "mail",
# }

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "cn=active,ou=groups",
#     "is_staff": "cn=staff,ou=groups",
#     "is_superuser": "cn=superuser,ou=groups"
# }

# # A tuple of django model fields used to uniquely identify a user.
# LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# # Path to a callable that takes a dict of {model_field_name: value},
# # returning a dict of clean model data.
# # Use this to customize how data loaded from LDAP is saved to the User model.
# LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"

# # Path to a callable that takes a user model and a dict of {ldap_field_name: [value]},
# # and saves any additional user relationships based on the LDAP data.
# # Use this to customize how data loaded from LDAP is saved to User model relations.
# # For customizing non-related User model fields, use LDAP_AUTH_CLEAN_USER_DATA.
# LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"

# # Path to a callable that takes a dict of {ldap_field_name: value},
# # returning a list of [ldap_search_filter]. The search filters will then be AND'd
# # together when creating the final search filter.
# LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"

# # Path to a callable that takes a dict of {model_field_name: value}, and returns
# # a string of the username to bind to the LDAP server.
# # Use this to support different types of LDAP server.
# # LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_openldap"
# LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory_principal"

# # Sets the login domain for Active Directory users.
# # LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = None
# LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "it.kmitl.ac.th"

# # The LDAP username and password of a user for querying the LDAP database for user
# # details. If None, then the authenticated user will be used for querying, and
# # the `ldap_sync_users` command will perform an anonymous query.
# LDAP_AUTH_CONNECTION_USERNAME = None
# LDAP_AUTH_CONNECTION_PASSWORD = None

# # Set connection/receive timeouts (in seconds) on the underlying `ldap3` library.
# LDAP_AUTH_CONNECT_TIMEOUT = None
# LDAP_AUTH_RECEIVE_TIMEOUT = None


#check SQL query.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    "loggers": {
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# Application definition

INSTALLED_APPS = [
    'core',
    'database_management',
    'analysis_data',
    'django_python3_ldap',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': ["templates"], 
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     'apptemplates.Loader',
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            # ],
        },
    },
]


WSGI_APPLICATION = 'Project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'senoir_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/'

APPEND_SLASH = True