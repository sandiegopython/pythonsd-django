from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views import generic
from revproxy.views import ProxyView

from .views import MeetupWidget


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', generic.RedirectView.as_view(url='/index.html', permanent=False), name='home'),
    url(r'^meetup-widget\.(?P<format>html|json)$', MeetupWidget.as_view(), name='meetup-widget'),
    url(r'coc/?$', generic.RedirectView.as_view(url='/pages/code-of-conduct.html')),
    url(r'^(?P<path>.*)$', ProxyView.as_view(upstream=settings.PYTHONSD_STATIC_SITE)),
]
