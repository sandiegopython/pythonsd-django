"""
Production settings for the pythonsd project.

In keeping with the 12 Factor App (https://12factor.net),
production settings come from the environment.
"""

import os

import dj_database_url

from .base import *  # noqa


# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = [
    "127.0.0.1",
    "pythonsd.org",
    "www.pythonsd.org",
    "pythonsd.com",
    "www.pythonsd.com",
    "sandiegopython.org",
    "www.sandiegopython.org",
    "pythonsd.herokuapp.com",
]


# Set the URL where the admin is accessible
ADMIN_URL = os.environ.get("ADMIN_URL", "admin")


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {"default": dj_database_url.config()}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 600


# Caching
# https://docs.djangoproject.com/en/1.11/ref/settings/#caches
# http://niwinz.github.io/django-redis/

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}


# Security
# https://docs.djangoproject.com/en/1.11/topics/security/
# https://devcenter.heroku.com/articles/http-routing#heroku-headers

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_HOST = os.environ.get("SECURE_SSL_HOST")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# If set, all requests to other domains redirect to this one
# https://github.com/dabapps/django-enforce-host
ENFORCE_HOST = os.environ.get("ENFORCE_HOST", None)


# Sessions
# https://docs.djangoproject.com/en/1.11/topics/http/sessions/
# Don't put sessions in the database

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
