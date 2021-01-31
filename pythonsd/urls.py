from django.urls import path
from django.views import generic

from .views import MeetupWidget


urlpatterns = [
    path(
        "",
        generic.RedirectView.as_view(url="/index.html", permanent=False),
        name="home",
    ),
    path(
        "meetup-widget.<str:format>",
        MeetupWidget.as_view(),
        name="meetup-widget",
    ),
    path("coc", generic.RedirectView.as_view(url="/pages/code-of-conduct.html")),
    path("coc/", generic.RedirectView.as_view(url="/pages/code-of-conduct.html")),
    # url(r'^newsite/coc/$', generic.TemplateView.as_view(template_name='pythonsd/pages/code-of-conduct.html')),
]
