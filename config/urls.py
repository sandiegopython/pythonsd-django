from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path


urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", include("pythonsd.urls")),
]


if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [path("__debug__", include(debug_toolbar.urls))] + urlpatterns
