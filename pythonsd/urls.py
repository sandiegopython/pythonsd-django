from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.urls import re_path
from django.views import generic

from . import views
from .sitemap import IndexSitemap
from .sitemap import StaticViewSitemap


sitemaps = {
    "index": IndexSitemap,
    "static": StaticViewSitemap,
}


urlpatterns = [
    path(
        r"",
        views.HomePageView.as_view(template_name="pythonsd/index.html"),
        name="index",
    ),
    path(
        r"code-of-conduct/",
        generic.TemplateView.as_view(template_name="pythonsd/code-of-conduct.html"),
        name="code-of-conduct",
    ),
    path(
        r"organizers/",
        views.OrganizersView.as_view(template_name="pythonsd/organizers.html"),
        name="organizers",
    ),
    # XHR/Async requests
    path(r"xhr/events/", views.UpcomingEventsView.as_view(), name="upcoming_events"),
    path(r"xhr/videos/", views.RecentVideosView.as_view(), name="recent_videos"),
    path(
        r"sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# These redirects handle redirecting URLs from the old static site to the new Django site
redirects = [
    re_path(
        r"^coc/?$",
        generic.RedirectView.as_view(url="/code-of-conduct/", permanent=False),
    ),
    path(
        r"pages/code-of-conduct.html",
        generic.RedirectView.as_view(url="/code-of-conduct/", permanent=False),
    ),
    # These pages were removed when we transitioned to the old GitHub pages based site
    path(r"index.html", generic.RedirectView.as_view(url="/", permanent=False)),
    path(
        r"pages/chat-room.html",
        generic.RedirectView.as_view(url="/#slack-channel", permanent=False),
    ),
    path(
        r"pages/workshops.html",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
    path(
        r"pages/getting-started.html",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
    path(
        r"pages/job-posting-guidelines.html",
        generic.RedirectView.as_view(url="/", permanent=False),
    ),
    # URL shortcuts for popular external links
    path(
        r"discord/",
        generic.RedirectView.as_view(
            url="https://discord.gg/8GpWuVvdbQ",
            permanent=False,
        ),
        name="redirect_discord",
    ),
    path(
        r"youtube/",
        generic.RedirectView.as_view(
            url="https://www.youtube.com/@sandiegopython/streams",
            permanent=False,
        ),
        name="redirect_youtube",
    ),
    path(
        r"present/",
        generic.RedirectView.as_view(
            url="https://docs.google.com/forms/d/e/1FAIpQLSfBUQjcSrnG7Afi-Uz6ewgFz45Vquea2Vj5egTEmTmoUAUHSg/viewform",
            permanent=False,
        ),
        name="redirect_presentation",
    ),
]

urlpatterns += redirects
