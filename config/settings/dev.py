"""
Local development settings for the pythonsd project.

These settings add some additional debugging features unsuitable for production.
"""

from .base import *  # noqa


# Enable Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io
# --------------------------------------------------------------------------
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE


# Enable template debugging (required for template coverage)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
