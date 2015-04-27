from django.conf.urls import include, url
from django.contrib import admin

from homepage.views import home_view

urlpatterns = [
    url(r'^$', home_view, name='home'),

    url(r'^admin/', include(admin.site.urls)),
]
