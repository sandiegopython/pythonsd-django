from datetime import datetime, timezone

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class IndexSitemap(Sitemap):
	changefreq = 'weekly'
	protocol = 'https'
	lastmod = datetime(2024, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
	priority = 1.0

	def items(self):
		return [
			'index',
		]

	def location(self, item):
		return reverse(item)


class StaticViewSitemap(Sitemap):
	changefreq = 'monthly'
	protocol = 'https'
	lastmod = datetime(2024, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
	priority = 0.8

	def items(self):
		return [
			'code-of-conduct',
		]

	def location(self, item):
		return reverse(item)
