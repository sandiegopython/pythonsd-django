from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from revproxy.views import ProxyView


urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", include("pythonsd.urls")),
    # Proxy all unmatched requests to the static Pelican site
    # This rule should come absolutely last
    path("<path:path>", ProxyView.as_view(upstream=settings.PYTHONSD_STATIC_SITE)),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [path("__debug__", include(debug_toolbar.urls))] + urlpatterns
