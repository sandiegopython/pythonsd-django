from django.conf.urls import url
from django.views import generic

from .views import HomePageView


urlpatterns = [
    url(r"^$", HomePageView.as_view(template_name="pythonsd/index.html"), name="index"),
    url(
        r"^code-of-conduct/$",
        generic.TemplateView.as_view(template_name="pythonsd/code-of-conduct.html"),
        name="code-of-conduct",
    ),
]

# These redirects handle redirecting URLs from the old static site to the new Django site
redirects = [
    url(
        r"^coc/?$",
        generic.RedirectView.as_view(url="/code-of-conduct/", permanent=False),
    ),
    url(
        r"^pages/code-of-conduct.html$",
        generic.RedirectView.as_view(url="/code-of-conduct/", permanent=False),
    ),
    # These pages were removed when we transitioned to the old GitHub pages based site
    url(r"^index.html$", generic.RedirectView.as_view(url="/", permanent=False)),
    url(
        r"^pages/chat-room.html$",
        generic.RedirectView.as_view(url="/#slack-channel", permanent=False),
    ),
    url(
        r"^pages/workshops.html$",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
    url(
        r"^pages/getting-started.html$",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
    url(
        r"^pages/job-posting-guidelines.html$",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
]

urlpatterns += redirects
