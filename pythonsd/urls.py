from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.views import generic
from revproxy.views import ProxyView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', generic.RedirectView.as_view(url='index.html', permanent=False)),
    url(r'^(?P<path>.*)$', ProxyView.as_view(upstream='http://pythonsd.github.io/pythonsd.org/'))
]

if settings.DEBUG:
    urlpatterns.extend(static.static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    ))
