from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^raffle$', views.raffle_view),
]
