from datetime import datetime
import logging

from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

import pytz
import requests


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
