from datetime import datetime
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.generic import TemplateView
import pytz
import requests


log = logging.getLogger(__file__)


class HomePageView(TemplateView):

    """
    Handles the homepage view including querying meetup.com for upcoming events

    - Handles caching meetup API requests to meetup so we don't get rate limited
    """

    cache_duration = 60 * 15
    cache_key = "pythonsd.views.MeetupWidget"
    template_name = "pythonsd/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming_events"] = self.get_upcoming_events()
        return context

    def get_upcoming_events(self):
        events = cache.get(self.cache_key)
        if events:
            log.debug("Using Meetup.com events from cache")
            return events

        log.debug("Requesting upcoming events from Meetup.com")

        # https://www.meetup.com/meetup_api/docs/:urlname/events/
        try:
            resp = requests.get(
                "https://api.meetup.com/pythonsd/events",
                params={"photo-host": "public", "page": "3"},
                timeout=5,
            )
        except Exception:
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
            cache.set(self.cache_key, events, self.cache_duration)
            return events

        return []
