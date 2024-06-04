"""Settings used in testing."""

import warnings

from .dev import *  # noqa


TESTING = True

STORAGES = {
    # In-memory storage makes tests marginally faster!
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    # Whitenoise relies on the manifest being present.
    # Which may not be there in testing
    # unless you run `collectstatic` before running tests
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# Ignore whitenoise message about no static directory
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
