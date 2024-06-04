"""
Production settings for the pythonsd project.

In keeping with the 12 Factor App (https://12factor.net),
production settings come from the environment.
"""

import os

import dj_database_url

from .base import *  # noqa


# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
    "localhost",
    "pythonsd.org",
    "www.pythonsd.org",
    "pythonsd.com",
    "www.pythonsd.com",
    "sandiegopython.org",
    "www.sandiegopython.org",
    "pythonsd-django.fly.dev",
]


# Set the URL where the admin is accessible
ADMIN_URL = os.environ.get("ADMIN_URL", "admin")


# Django-storages
# https://django-storages.readthedocs.io
# --------------------------------------------------------------------------
# Optionally store media files in S3/R2/etc.
AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
# When using media storage with a custom domain
# set this and set MEDIA_URL
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
# The endpoint URL is necessary for Cloudflare R2
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", default=None)
if AWS_S3_ACCESS_KEY_ID and AWS_S3_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# --------------------------------------------------------------------------
DATABASES = {"default": dj_database_url.config()}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 600


# Caching
# https://docs.djangoproject.com/en/4.2/ref/settings/#caches
# http://niwinz.github.io/django-redis/
# --------------------------------------------------------------------------
if "REDIS_URL" in os.environ:
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
# https://docs.djangoproject.com/en/4.2/topics/security/
# --------------------------------------------------------------------------
if "SECURE_SSL_HOST" in os.environ:
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
# https://docs.djangoproject.com/en/4.2/topics/http/sessions/
# Don't put sessions in the database

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"


# Email
# https://docs.djangoproject.com/en/4.2/topics/email/
# https://anymail.readthedocs.io/en/stable/
# --------------------------------------------------------------------------
if "SENDGRID_API_KEY" in os.environ:
    INSTALLED_APPS += ["anymail"]
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {"SENDGRID_API_KEY": os.environ["SENDGRID_API_KEY"]}


# Logging
# http://docs.djangoproject.com/en/4.2/topics/logging
# --------------------------------------------------------------------------
LOGGING["loggers"][""]["level"] = "INFO"
LOGGING["loggers"]["pythonsd"]["level"] = "INFO"
