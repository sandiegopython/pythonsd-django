"""General tests for site setup and functionality.

Specific tests relating to one app should be in that package.
"""

import json
import os
import unittest
from unittest import mock

from django import test
from django.core.cache import cache
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import responses
import webtest

from config import wsgi
from ..views import RecentVideosView
from ..views import UpcomingEventsView
from ..models import Organizer


# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class TestBasicViews(test.TestCase):
    def test_code_of_conduct(self):
        response = self.client.get(reverse("code-of-conduct"))
        self.assertContains(response, "<h1>Code of Conduct</h1>")

    def test_coc_redirect(self):
        """The shortcuts '/coc' and '/coc/' paths should redirect to
        the code of conduct page."""
        response = self.client.get("/coc")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/code-of-conduct/")

        response = self.client.get("/coc/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/code-of-conduct/")


class TestHomepageView(test.TestCase):
    def test_homepage(self):
        response = self.client.get(reverse("index"))
        self.assertContains(
            response,
            "San Diego Python is a Python programming language special interest group",
        )


class TestOrganizersView(test.TestCase):
    def test_organizers(self):
        org1 = Organizer(
            name="First organizer",
            meetup_url="http://example.com/meetup",
            linkedin_url="http://example.com/linkedin",
            active=True,
            photo=SimpleUploadedFile(
                name="test.png", content=ONE_PIXEL_PNG_BYTES, content_type="image/png"
            ),
        )
        org1.save()

        org2 = Organizer(
            name="Second organizer",
            meetup_url="http://example.com/meetup",
            active=False,
            photo=SimpleUploadedFile(
                name="test.png", content=ONE_PIXEL_PNG_BYTES, content_type="image/png"
            ),
        )
        org2.save()

        response = self.client.get(reverse("organizers"))
        self.assertContains(response, "<h1>Organizers</h1>")
        self.assertContains(response, org1.name)
        self.assertNotContains(response, org2.name)


class TestMeetupEventsView(test.TestCase):
    def setUp(self):
        self.url = reverse("upcoming_events")

        fp = os.path.join(os.path.dirname(__file__), "data/meetup-events-api.json")
        with open(fp) as fd:
            self.api_response = json.load(fd)

        self.expected_events = [
            {
                "id": "305930677",
                "link": "https://www.meetup.com/pythonsd/events/305930677/",
                "name": "SDPy Monthly Meetup",
                "datetime": "2025-05-22T19:00:00-07:00",
                "venue": "Qualcomm Building Q",
            },
            {
                "id": "305930676",
                "link": "https://www.meetup.com/pythonsd/events/305930676/",
                "name": "SDPy Monthly Meetup",
                "datetime": "2025-06-26T19:00:00-07:00",
                "venue": "Qualcomm Building Q",
            },
            {
                "id": "305930675",
                "link": "https://www.meetup.com/pythonsd/events/305930675/",
                "name": "SDPy Monthly Meetup",
                "datetime": "2025-07-24T19:00:00-07:00",
                "venue": "Qualcomm Building Q",
            },
        ]

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_no_events(self):
        with mock.patch(
            "pythonsd.views.UpcomingEventsView.get_upcoming_events", return_value=[]
        ) as mock_get:
            response = self.client.get(self.url)
            self.assertContains(response, "There are no upcoming events")

    def test_preloaded_events(self):
        with mock.patch(
            "pythonsd.views.UpcomingEventsView.get_upcoming_events",
            return_value=self.expected_events,
        ) as mock_get:
            response = self.client.get(self.url)
            self.assertContains(response, "Qualcomm Building Q")
            self.assertContains(response, "SDPy Monthly Meetup")

    @responses.activate
    def test_html_widget(self):
        responses.add(
            responses.POST,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            json=self.api_response,
            status=200,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "Qualcomm Building Q")
        self.assertContains(response, "SDPy Monthly Meetup")

    @responses.activate
    def test_api_noevents(self):
        responses.add(
            responses.POST,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            json={"data": {"groupByUrlname": {"events": {"edges": []}}}},
            status=400,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "There are no upcoming events")

    @responses.activate
    def test_api_exception(self):
        responses.add(
            responses.POST,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            body=Exception("Error connecting..."),
        )

        response = self.client.get(self.url)
        self.assertContains(response, "There are no upcoming events")

    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.POST,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            json={"errors": ["There was some error querying meetup.com"]},
        )

        response = self.client.get(self.url)
        self.assertContains(response, "There are no upcoming events")


class TestYouTubeRecentVideosView(test.TestCase):
    def setUp(self):
        self.url = reverse("recent_videos")

        fp = os.path.join(os.path.dirname(__file__), "data/youtube-video-feed.xml")
        with open(fp) as fd:
            self.api_response = fd.read()

        self.expected_videos = [
            {
                # These are actually datetime.datetimes
                "datetime": "2023-01-27T17:52:55Z",
                "id": "MvpiCyPpAhM",
                "title": "San Diego Python Monthly Meetup January 2023",
                "url": "https://www.youtube.com/watch?v=MvpiCyPpAhM",
            },
            {
                "datetime": "2022-12-22T13:55:08Z",
                "id": "qyfmJVBZFIQ",
                "title": "San Diego Python Monthly Meetup December 2022",
                "url": "https://www.youtube.com/watch?v=qyfmJVBZFIQ",
            },
        ]

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_no_videos(self):
        with mock.patch(
            "pythonsd.views.RecentVideosView.get_recent_videos", return_value=[]
        ) as mock_get:
            response = self.client.get(self.url)
            self.assertContains(response, "Check out our")

    def test_preloaded_videos(self):
        with mock.patch(
            "pythonsd.views.RecentVideosView.get_recent_videos",
            return_value=self.expected_videos,
        ) as mock_get:
            response = self.client.get(self.url)
            self.assertContains(response, "MvpiCyPpAhM")
            self.assertContains(response, "<iframe")
            self.assertNotContains(response, "qyfmJVBZFIQ")

    @responses.activate
    def test_html_video_widget(self):
        responses.add(
            responses.GET,
            RecentVideosView.YOUTUBE_FEED_URL,
            body=self.api_response,
            status=200,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "MvpiCyPpAhM")
        self.assertContains(response, "<iframe")
        self.assertNotContains(response, "qyfmJVBZFIQ")

    @responses.activate
    def test_api_novideos(self):
        responses.add(
            responses.GET,
            RecentVideosView.YOUTUBE_FEED_URL,
            status=400,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "Check out our")

    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.GET,
            RecentVideosView.YOUTUBE_FEED_URL,
            body=Exception("Error connecting..."),
        )

        response = self.client.get(self.url)
        self.assertContains(response, "Check out our")


class TestSitemap(test.TestCase):
    def test_sitemap(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)


class TestWSGIApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = webtest.TestApp(wsgi.application)

    def test_admin_login(self):
        """Test that the admin login can be reached through the WSGI App.

        This test is mostly to exercise the interface.
        """
        response = self.app.get("/admin/login/")
        self.assertEqual(response.status_int, 200)
