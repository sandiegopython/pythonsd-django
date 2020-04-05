"""General tests for site setup and functionality.

Specific tests relating to one app should be in that package.
"""

import json
import os
import unittest
from unittest import mock

from django import test
from django.conf import settings
from django.urls import reverse
import webtest

from config import wsgi


class TestBasicViews(test.TestCase):
    def test_code_of_conduct(self):
        response = self.client.get(reverse("code-of-conduct"))
        self.assertContains(response, "<h1>Code of Conduct</h1>")

    def test_coc_redirect(self):
        """The shortcut '/coc' path should redirect to
        the code of conduct page."""
        response = self.client.get("/coc")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/code-of-conduct/")


class TestHomepageMeetupEvents(test.TestCase):
    def setUp(self):
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

    @mock.patch("pythonsd.views.HomePageView.get_upcoming_events", return_value=[])
    def test_no_events(self, mock_call):
        response = self.client.get("/")
        self.assertContains(response, "There are no upcoming events")

    def test_html_widget(self):
        with mock.patch("pythonsd.views.requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = self.api_response
            response = self.client.get("/")
        self.assertContains(response, "UCSD Geisel Library")
        self.assertContains(response, "Qualcomm Building Q")

        # Check that it is retreived from the cache
        with mock.patch("pythonsd.views.requests.get") as mock_get:
            mock_get.return_value.ok = (
                False
            )  # Return val shouldn't matter - using cache
            response = self.client.get("/")
        self.assertContains(response, "UCSD Geisel Library")

    def test_api_failure(self):
        with mock.patch("pythonsd.views.requests.get") as mock_get:
            mock_get.return_value.ok = False
            response = self.client.get("/")
            self.assertContains(response, "There are no upcoming events")

        with mock.patch("pythonsd.views.requests.get") as mock_get:
            mock_get.side_effect = Exception
            response = self.client.get("/")
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
