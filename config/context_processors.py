"""Custom context processors that inject certain settings values into all templates."""

from django.conf import settings


def settings_processor(request):
    return {
        "APP_VERSION": settings.APP_VERSION,
        "APP_REVISION": settings.APP_REVISION,
    }
