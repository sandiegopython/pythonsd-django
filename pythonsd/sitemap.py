from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Meetup


class IndexSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 1.0

    def items(self):
        return [
            "index",
        ]

    def location(self, item):
        return reverse(item)


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"
    priority = 0.8

    def items(self):
        return [
            "code-of-conduct",
        ]

    def location(self, item):
        return reverse(item)


class MeetupYearSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"
    priority = 0.7

    def items(self):
        return [d.year for d in Meetup.objects.dates("date", "year", order="DESC")]

    def location(self, item):
        return reverse("meetup_year", kwargs={"year": item})
