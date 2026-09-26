import hmac
import logging
import zoneinfo
from datetime import datetime

import requests
from defusedxml import ElementTree
from django.conf import settings
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import Meetup
from .models import Organizer
from .models import Sponsor
from .youtube import fetch_and_sync_youtube_feed


CACHE_DURATION = 60 * 15  # 15 minutes
log = logging.getLogger(__file__)


class HomePageView(TemplateView):
    """Displays the homepage."""

    template_name = "pythonsd/index.html"

    # Maximum number of sponsors to show on the homepage
    MAX_SPONSORS = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sponsors"] = Sponsor.objects.filter(active=True).order_by("order")[
            : self.MAX_SPONSORS
        ]
        return context


class OrganizersView(TemplateView):
    """Displays SD Python organizers."""

    template_name = "pythonsd/organizers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organizers"] = Organizer.objects.filter(active=True).order_by("name")
        return context


@method_decorator(cache_page(CACHE_DURATION), name="dispatch")
class UpcomingEventsView(TemplateView):
    """Get upcoming events from Meetup."""

    # https://www.meetup.com/api/guide/
    MEETUP_EVENT_API_URL = "https://api.meetup.com/gql-ext"

    # https://www.meetup.com/pythonsd/
    MEETUP_GROUP_SLUG = "pythonsd"

    template_name = "pythonsd/fragments/upcoming-events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming_events"] = self.get_upcoming_events()
        return context

    def get_upcoming_events(self):
        """Get upcoming events from Meetup."""
        log.debug("Requesting upcoming events from Meetup.com")

        # Fetch the next 3 events from the API
        # https://www.meetup.com/api/schema/#Group
        # https://www.meetup.com/api/guide/#p02-querying-section
        body = """
          query($urlname: String!) {
            groupByUrlname(urlname: $urlname) {
              events(first: 3) {
                edges {
                  node {
                    id
                    title
                    venues {
                      name
                    }
                    eventUrl
                    dateTime
                  }
                }
              }
            }
          }
        """

        try:
            resp = requests.post(
                url=self.MEETUP_EVENT_API_URL,
                json={"query": body, "variables": {"urlname": self.MEETUP_GROUP_SLUG}},
                timeout=5,
            )
        except Exception:
            log.exception("Request error fetching Meetup event feed")
            return []

        if resp.ok:
            data = resp.json()

            if "errors" in data:
                log.error("GraphQL error fetching Meetup event feed: %s", data)
                return []

            # Transform from meetup's API format into our format
            events = []
            for edge in resp.json()["data"]["groupByUrlname"]["events"]["edges"]:
                event = edge["node"]
                events.append(
                    {
                        "id": event["id"],
                        "name": event["title"],
                        "link": event["eventUrl"],
                        # Meetup's API seems to return in our timezone
                        # but we'll be explicit here for future-proofing
                        "datetime": datetime.fromisoformat(
                            event["dateTime"]
                        ).astimezone(zoneinfo.ZoneInfo(key=settings.TIME_ZONE)),
                        # Technically an event can have multiple or no venue (it's an array)
                        "venue": (
                            event["venues"][0]["name"] if event["venues"] else None
                        ),
                    }
                )
            return events
        else:
            log.error(
                "Error fetching Meetup event feed (status code=%s)", resp.status_code
            )

        return []


@method_decorator(cache_page(CACHE_DURATION), name="dispatch")
class RecentVideosView(TemplateView):
    """Get recent videos from YouTube."""

    # Our channel ID (eg. https://www.youtube.com/channel/UCXU-oZwaHnoYUhja_yrrrGg)
    YOUTUBE_CHANNEL_ID = settings.YOUTUBE_CHANNEL_ID
    YOUTUBE_FEED_URL = settings.YOUTUBE_FEED_URL

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
                        ).astimezone(zoneinfo.ZoneInfo(key=settings.TIME_ZONE)),
                    }
                )
        else:
            log.error("Error fetching YouTube video feed")

        return videos


class MeetupsArchiveView(View):
    """Redirects /meetups/ to the most recent year with a meetup."""

    def get(self, request, *args, **kwargs):
        latest_year = (
            Meetup.objects.order_by("-date")
            .values_list("date__year", flat=True)
            .first()
        )
        if not latest_year:
            raise Http404("No meetups found.")
        return redirect("meetup_year", year=latest_year)


class MeetupYearView(TemplateView):
    """Displays all meetups and talks for a specific year."""

    template_name = "pythonsd/meetup_year.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs["year"]
        meetups = (
            Meetup.objects.filter(date__year=year)
            .prefetch_related("talks")
            .order_by("-date")
        )
        if not meetups.exists():
            raise Http404(f"No meetups found for year {year}")

        context["year"] = year
        context["meetups"] = meetups
        context["all_years"] = [
            d.year for d in Meetup.objects.dates("date", "year", order="DESC")
        ]
        return context


@method_decorator(csrf_exempt, name="dispatch")
class YouTubeIngestView(View):
    """Endpoint for ingesting YouTube videos via webhook."""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])

    def post(self, request, *args, **kwargs):
        secret = getattr(settings, "YOUTUBE_SYNC_SECRET", None)
        if not secret:
            return HttpResponseForbidden("Sync secret is not configured.")

        auth_header = request.headers.get("Authorization", "")
        expected_header = f"Bearer {secret}"

        if not hmac.compare_digest(auth_header, expected_header):
            return HttpResponseForbidden("Invalid or missing authorization token.")

        try:
            stats = fetch_and_sync_youtube_feed()
            return JsonResponse({"status": "ok", **stats})
        except Exception:
            log.exception("Error syncing YouTube feed")
            return JsonResponse(
                {"status": "error", "message": "Failed to sync YouTube feed"},
                status=500,
            )
