from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from homepage.views import home_view

urlpatterns = [
    url(r'^$', home_view, name='home'),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns.extend(static.static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    ))
