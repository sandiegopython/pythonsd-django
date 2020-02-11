from __future__ import absolute_import

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
import jinja2


def environment(**options):
    env = jinja2.Environment(**options)
    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
            "MEDIA_URL": settings.MEDIA_URL,
        }
    )
    return env
