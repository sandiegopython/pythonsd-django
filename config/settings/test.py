"""Settings used in testing."""
import warnings

from .dev import *  # noqa


TESTING = True

# Ignore whitenoise message about no static directory
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
