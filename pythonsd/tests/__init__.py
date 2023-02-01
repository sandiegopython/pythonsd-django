"""General tests for site setup and functionality.

Specific tests relating to one app should be in that package.
"""

import json
import os
import unittest
from unittest import mock

from django import test
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
import responses
import webtest

from config import wsgi
from ..views import UpcomingEventsView


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


class TestMeetupEventsView(test.TestCase):
    def setUp(self):
        self.url = reverse("upcoming_events")

        fp = os.path.join(os.path.dirname(__file__), "data/meetup-events-api.json")
        with open(fp) as fd:
            self.api_response = json.load(fd)

        self.expected_events = [
            {
                "link": "https://www.meetup.com/pythonsd/events/fdzbnqyznbqb/",
                "name": "Saturday Study Group",
                "datetime": "2019-10-12T12:00:00-07:00",
                "venue": "UCSD Geisel Library",
            },
            {
                "link": "https://www.meetup.com/pythonsd/events/fdzbnqyznbzb/",
                "name": "Saturday Study Group",
                "datetime": "2019-10-19T12:00:00-07:00",
                "venue": "UCSD Geisel Library",
            },
            {
                "link": "https://www.meetup.com/pythonsd/events/zgtnxqyznbgc/",
                "name": "Monthly Meetup",
                "datetime": "2019-10-24T19:00:00-07:00",
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
            self.assertContains(response, "UCSD Geisel Library")
            self.assertContains(response, "Qualcomm Building Q")

    @responses.activate
    def test_html_widget(self):
        responses.add(
            responses.GET,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            json=self.api_response,
            status=200,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "UCSD Geisel Library")
        self.assertContains(response, "Qualcomm Building Q")

    @responses.activate
    def test_api_noevents(self):
        responses.add(
            responses.GET,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            json=[],
            status=400,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "There are no upcoming events")

    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.GET,
            UpcomingEventsView.MEETUP_EVENT_API_URL,
            body=Exception("Error connecting..."),
        )

        response = self.client.get(self.url)
        self.assertContains(response, "There are no upcoming events")


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
