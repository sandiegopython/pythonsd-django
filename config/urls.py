from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r"^{}/".format(settings.ADMIN_URL), include(admin.site.urls)),
    url(r"^", include("pythonsd.urls")),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
