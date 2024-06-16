"""
Django settings for pythonsd project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import json
import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")

ADMIN_URL = "admin"


# Quick-start development settings - unsuitable for production
# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = "MOCK SECRET"
DEBUG = True


ALLOWED_HOSTS = ["*"]


INTERNAL_IPS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "pythonsd",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "enforce_host.EnforceHostMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.settings_processor",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# --------------------------------------------------------------------------
DATABASES = {"default": dj_database_url.config(default="sqlite:///db.sqlite3")}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-STORAGES
# --------------------------------------------------------------------------
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static-files/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets", "dist"),
    os.path.join(BASE_DIR, "pythonsd", "static"),
    # Only available after running `npm install`
    os.path.join(BASE_DIR, "node_modules/htmx.org/dist"),
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = os.environ.get("MEDIA_URL", default="/media/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Email
# https://docs.djangoproject.com/en/4.2/topics/email/
# --------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@sandiegopython.org"
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# http://docs.djangoproject.com/en/4.2/topics/logging
# https://docs.djangoproject.com/en/4.2/ref/settings/#logging
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "succinct": {
            "format": "{levelname} {asctime} [{name}] {message}",
            "style": "{",
        },
        "verbose": {
            "format": (
                "{levelname} {asctime} [{name}] "
                "{module}.{funcName}():{lineno:d} - {message}"
            ),
            "style": "{",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console-verbose": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "succinct",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "succinct",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
        "pythonsd": {
            "level": "DEBUG",
            "handlers": ["console-verbose"],
            "propagate": False,
        },
        "django": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# App specific configuration
# --------------------------------------------------------------------------
with open(os.path.join(BASE_DIR, "package.json"), encoding="utf-8") as fd:
    APP_VERSION = json.load(fd)["version"]

APP_REVISION = None
if os.path.exists(os.path.join(BASE_DIR, "GIT_COMMIT")):
    with open(os.path.join(BASE_DIR, "GIT_COMMIT"), encoding="utf-8") as fd:
        APP_REVISION = fd.read().strip()
