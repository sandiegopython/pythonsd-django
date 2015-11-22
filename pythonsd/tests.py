"""General tests for site setup and functionality.

Specific tests relating to one app should be in that package.
"""

import importlib
import subprocess
import unittest
from unittest import mock

from django import test
from django.conf import settings
import webtest

import pythonsd.settings
from . import jinja2, static_files, wsgi


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


class TestCompileFinder(unittest.TestCase):
    """Test the custom static 'Finder' class for static file compiling."""

    @mock.patch('subprocess.call', wraps=subprocess.call)
    def test_compile_collectstatic(self, mock_call):
        """A subprocess call to 'make' should be made."""
        compile_finder = static_files.CompileFinder()
        compile_finder.list('mock argument')
        mock_call.assert_called_with('make')


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
