import unittest
from unittest import mock

from django import test
from django.conf import settings

from . import jinja2, static_files


@mock.patch('revproxy.views.HTTP_POOLS.urlopen', return_value=mock.MagicMock(status=200))
class TestProxyViews(test.TestCase):

    def test_home(self, mock_urlopen):
        mock_path = 'mock-path'
        self.client.get('/' + mock_path, follow=True)
        args, kwargs = mock_urlopen.call_args
        self.assertEqual(args[1], settings.PYTHONSD_STATIC_SITE + mock_path)


class TestJinjaConfig(unittest.TestCase):

    def test_jinja_env(self):
        expected_subset = {'static', 'url', 'MEDIA_URL'}
        full_environment = jinja2.environment().globals
        self.assertTrue(
            expected_subset.issubset(full_environment),
            'Missing values: {}'.format(expected_subset.difference(full_environment)),
        )


class TestCompileFinder(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_compile_collectstatic(self, mock_call):
        compile_finder = static_files.CompileFinder()
        compile_finder.list('mock argument')
        mock_call.assert_called_with('make')
