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
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = [
    '127.0.0.1',
    'pythonsd.org',
    'www.pythonsd.org',
    'pythonsd.com',
    'www.pythonsd.com',
    'sandiegopython.org',
    'www.sandiegopython.org',
    'pythonsd.herokuapp.com',
]


# Set the URL where the admin is accessible
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin')


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(),
}
