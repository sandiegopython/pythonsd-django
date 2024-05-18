from datetime import datetime
import logging

from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

import pytz
import requests
from defusedxml import ElementTree


CACHE_DURATION = 60 * 15  # 15 minutes
log = logging.getLogger(__file__)


class HomePageView(TemplateView):
    """Displays the homepage."""

    template_name = "pythonsd/index.html"


@method_decorator(cache_page(CACHE_DURATION), name="dispatch")
class UpcomingEventsView(TemplateView):
    """Get upcoming events from Meetup."""

    MEETUP_EVENT_API_URL = "https://api.meetup.com/pythonsd/events"

    template_name = "pythonsd/fragments/upcoming-events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming_events"] = self.get_upcoming_events()
        return context

    def get_upcoming_events(self):
        """Get upcoming events from Meetup."""
        log.debug("Requesting upcoming events from Meetup.com")

        # https://www.meetup.com/meetup_api/docs/:urlname/events/
        try:
            resp = requests.get(
                self.MEETUP_EVENT_API_URL,
                params={"photo-host": "public", "page": "3"},
                timeout=5,
            )
        except Exception:
            log.exception("Request error fetching Meetup event feed")
            return []

        if resp.ok:
            # Transform from meetup's API format into our format
            events = [
                {
                    "link": e["link"],
                    "name": e["name"],
                    # Always show time in local San Diego time
                    "datetime": datetime.utcfromtimestamp(e["time"] // 1000)
                    .replace(tzinfo=pytz.utc)
                    .astimezone(pytz.timezone(settings.TIME_ZONE)),
                    "venue": e["venue"]["name"] if "venue" in e else None,
                }
                for e in resp.json()
            ]
            return events
        else:
            log.error("Error fetching Meetup event feed")

        return []


@method_decorator(cache_page(CACHE_DURATION), name="dispatch")
class RecentVideosView(TemplateView):
    """Get recent videos from YouTube."""

    # Our channel ID (eg. https://www.youtube.com/channel/UCXU-oZwaHnoYUhja_yrrrGg)
    YOUTUBE_CHANNEL_ID = "UCXU-oZwaHnoYUhja_yrrrGg"
    YOUTUBE_FEED_URL = (
        f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    )

    template_name = "pythonsd/fragments/recent-videos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_videos"] = self.get_recent_videos()
        return context

    def get_recent_videos(self):
        """Get recent videos from YouTube."""
        log.debug("Requesting recent videos feed from YouTube")

        try:

            resp = requests.get(self.YOUTUBE_FEED_URL, timeout=5)
        except Exception:
            # This is a broad exception because this can throw a pretty wide range
            # of exceptions. Most are from requests.errors unless it's a lower
            # level exception like an SSLError or something like that.
            log.exception("Request error fetching YouTube video feed")
            return []

        videos = []
        if resp.ok:
            dom = ElementTree.fromstring(resp.content)
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "yt": "http://www.youtube.com/xml/schemas/2015",
            }
            for entry in dom.findall("atom:entry", ns):
                videos.append(
                    {
                        "id": entry.find("yt:videoId", ns).text,
                        "title": entry.find("atom:title", ns).text,
                        "url": entry.find("atom:link", ns).attrib["href"],
                        # The updated date can change
                        # But for live streams, the published date is the date
                        # the stream was initialized in youtube, not when it was live
                        "datetime": datetime.fromisoformat(
                            entry.find("atom:updated", ns).text
                        ).astimezone(pytz.timezone(settings.TIME_ZONE)),
                    }
                )
        else:
            log.error("Error fetching YouTube video feed")

        return videos
