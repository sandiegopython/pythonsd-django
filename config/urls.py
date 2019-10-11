from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from revproxy.views import ProxyView


urlpatterns = [
    url(r'^{}/'.format(settings.ADMIN_URL), include(admin.site.urls)),

    url(r'^', include('pythonsd.urls')),

    # Proxy all unmatched requests to the static Pelican site
    # This rule should come absolutely last
    url(r'^(?P<path>.*)$', ProxyView.as_view(upstream=settings.PYTHONSD_STATIC_SITE)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
