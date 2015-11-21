from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.views import generic
from revproxy.views import ProxyView

import raffle.urls

urlpatterns = [
    url(r'', include(raffle.urls)),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', generic.RedirectView.as_view(url='index.html', permanent=False), name='home'),
    url(r'^(?P<path>.*)$', ProxyView.as_view(upstream=settings.PYTHONSD_STATIC_SITE))
]

if settings.DEBUG:
    urlpatterns.extend(static.static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    ))
