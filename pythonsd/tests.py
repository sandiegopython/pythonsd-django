"""General tests for site setup and functionality.

Specific tests relating to one app should be in that package.
"""

import importlib
import json
import os
import shutil
import stat
import unittest
from unittest import mock

from django import test
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.utils import timezone
import webtest

import pythonsd.settings
import tasks
from . import jinja2, static_files, wsgi


class TestRedirectViews(test.TestCase):
    """Ensure project redirects function correctly."""

    def test_home_redirect(self):
        """The root path '/' should redirect to '/index.html'
        in order to work with the reverse proxy.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/index.html')

    def test_coc_redirect(self):
        """The shortcut '/coc' path should redirect to
        the code of conduct page."""
        response = self.client.get('/coc')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/pages/code-of-conduct.html')


class TestMeetupWidget(test.TestCase):
    """Test the Meetup.com widget of upcoming events"""

    def setUp(self):
        self.event1 = {
            "link": "https://example.com/event-1/",
            "name": "Event #1",
            "datetime": timezone.now(),
            "venue": "Venue #1",
        }
        self.event2 = {
            "link": "https://example.com/event-2/",
            "name": "Event #2",
            "datetime": timezone.now(),
            "venue": "Venue #2",
        }
        self.expected_events = [self.event1, self.event2]

    @mock.patch('pythonsd.views.MeetupWidget.get_upcoming_events', return_value=[])
    def test_no_events(self, mock_call):
        response = self.client.get('/meetup-widget.html')
        self.assertContains(response, 'No upcoming events')

    def test_html_widget(self):
        with mock.patch('pythonsd.views.MeetupWidget.get_upcoming_events', return_value=self.expected_events) as _:
            response = self.client.get('/meetup-widget.html')
        self.assertTrue('text/html' in response['Content-Type'])
        self.assertContains(response, 'Event #1')
        self.assertContains(response, 'Event #2')

    def test_json_widget(self):
        with mock.patch('pythonsd.views.MeetupWidget.get_upcoming_events', return_value=self.expected_events) as _:
            response = self.client.get('/meetup-widget.json')
        expected = json.dumps(self.expected_events, cls=DjangoJSONEncoder)
        self.assertJSONEqual(response.content, expected)


@mock.patch('revproxy.views.HTTP_POOLS.urlopen', return_value=mock.MagicMock(status=200))
class TestProxyViews(test.TestCase):
    """Any path not served by this Django app should proxy to the static site."""

    def test_unserved_path(self, mock_urlopen):
        """Any path without a normal URL pattern should default to the proxy view."""
        mock_path = 'mock-path'
        self.client.get('/' + mock_path, follow=True)
        args, kwargs = mock_urlopen.call_args
        self.assertEqual(args[1], settings.PYTHONSD_STATIC_SITE + mock_path)


class TestJinjaConfig(unittest.TestCase):
    """Make sure the Jinja configuration is complete."""

    def test_jinja_env(self):
        """Ensure certain settings are in the Jinja environment."""
        expected_subset = {'static', 'url', 'MEDIA_URL'}
        full_environment = jinja2.environment().globals
        self.assertTrue(
            expected_subset.issubset(full_environment),
            'Missing values: {}'.format(expected_subset.difference(full_environment)),
        )


class TestCSSCompiling(unittest.TestCase):
    """Test the custom static 'Finder' class for static file compiling."""

    @mock.patch('tasks.build', wraps=tasks.build)
    def test_compile_collectstatic(self, mock_call):
        """A subprocess call to 'make' should be made."""
        compile_finder = static_files.CompileFinder()
        compile_finder.list('mock argument')
        mock_call.assert_called_once_with()

    def test_missing_destination(self):
        shutil.rmtree(tasks.CSS_DIR)
        tasks.build()

    def test_existing_desintation(self):
        shutil.rmtree(tasks.CSS_DIR)
        os.makedirs(tasks.CSS_DIR)
        tasks.build()

    @mock.patch('os.makedirs', side_effect=OSError)
    def test_other_exception(self, mock_makedirs):
        self.assertRaises(OSError, tasks.build)


class TestDebugMode(unittest.TestCase):
    """Check that the correct DEBUG state is set in each environment."""

    @classmethod
    def setUpClass(cls):
        cls.settings = pythonsd.settings

    @classmethod
    def tearDownClass(cls):
        importlib.reload(cls.settings)

    def test_debug_default_on(self):
        """DEBUG should be True when there is no SECRET_KEY"""
        mock_environ = {}
        with mock.patch('os.environ', mock_environ):
            importlib.reload(self.settings)
        self.assertIs(self.settings.DEBUG, True)

    def test_debug_off(self):
        """DEBUG should be False when there is a SECRET_KEY

        Presence of SECRET_KEY indicates a production environment.
        """
        mock_environ = {'SECRET_KEY': 'some test secret'}
        with mock.patch('os.environ', mock_environ):
            importlib.reload(self.settings)
        self.assertIs(self.settings.DEBUG, False)


class TestWSGIApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = webtest.TestApp(wsgi.application)

    def test_admin_login(self):
        """Test that the admin login can be reached through the WSGI App.

        This test is mostly to exercise the interface.
        """
        response = self.app.get('/admin/login/')
        self.assertEqual(response.status_int, 200)
