from django.conf.urls import url
from django.views import generic

from .views import MeetupWidget


urlpatterns = [
    url(
        r"^$",
        generic.RedirectView.as_view(url="/index.html", permanent=False),
        name="home",
    ),
    url(
        r"^meetup-widget\.(?P<format>html|json)$",
        MeetupWidget.as_view(),
        name="meetup-widget",
    ),
    url(r"^coc/?$", generic.RedirectView.as_view(url="/pages/code-of-conduct.html")),
    # url(r'^newsite/coc/$', generic.TemplateView.as_view(template_name='pythonsd/pages/code-of-conduct.html')),
]
