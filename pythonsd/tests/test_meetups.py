import json
import tempfile
from datetime import date
from pathlib import Path
from unittest import mock

import responses
from django import test
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.urls import reverse

from ..models import Meetup
from ..models import Talk
from ..sitemap import MeetupYearSitemap
from ..youtube import extract_meetup_date
from ..youtube import fetch_and_sync_youtube_feed
from ..youtube import parse_meetup_description
from ..youtube import sync_meetup_record


SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/">

 <entry>
  <yt:videoId>test_vid_1</yt:videoId>
  <atom:title>September 2026 Monthly Meetup - San Diego Python</atom:title>
  <atom:published>2026-09-25T15:38:30+00:00</atom:published>
  <media:group>
   <media:description>This is our monthly meetup livestream from September 24, 2026.

https://www.meetup.com/pythonsd/events/312775789/

TIMESTAMPS
00:00 Waiting to start
04:08 Introductions
10:12 Jane User - Classes in Python
56:35 Outro</media:description>
  </media:group>
 </entry>
 <entry>
  <!-- Incomplete entry to test error resilience -->
  <atom:title>No Video ID</atom:title>
 </entry>
 <entry>
  <yt:videoId>test_vid_2</yt:videoId>
  <atom:title>August 2026 Monthly Meetup</atom:title>
  <atom:published>invalid-date-string</atom:published>
  <media:group>
   <media:description></media:description>
  </media:group>
 </entry>
 <entry>
  <yt:videoId>test_vid_3</yt:videoId>
  <atom:title>July 2026 Monthly Meetup</atom:title>
 </entry>
</feed>
"""


class TestMeetupViews(test.TestCase):
    def test_meetups_archive_empty(self):
        url = reverse("meetups_archive")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_meetups_archive_redirect_to_latest_year(self):
        # Create a 2025 meetup and a 2026 meetup
        Meetup.objects.create(
            title="November 2025 Monthly Meetup",
            date=date(2025, 11, 20),
            youtube_id="vid_2025",
        )
        Meetup.objects.create(
            title="September 2026 Monthly Meetup",
            date=date(2026, 9, 24),
            youtube_id="vid_2026",
        )
        url = reverse("meetups_archive")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/meetups/2026/")

    def test_meetup_year_view(self):
        meetup = Meetup.objects.create(
            title="September 2026 Monthly Meetup",
            date=date(2026, 9, 24),
            youtube_id="fM-P0ZLY-_U",
            meetup_url="https://www.meetup.com/pythonsd/events/312775789/",
        )
        Talk.objects.create(
            meetup=meetup,
            speaker_name="Jane User",
            title="Classes in Python",
            timestamp_seconds=612,
            timestamp_label="10:12",
        )

        # Meetup without talks
        Meetup.objects.create(
            title="August 2026 Monthly Meetup",
            date=date(2026, 8, 27),
            youtube_id="VrtT15hlWXw",
        )

        url = reverse("meetup_year", kwargs={"year": 2026})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026 Meetups")
        self.assertContains(response, "September 2026 Monthly Meetup")
        self.assertContains(response, "August 2026 Monthly Meetup")
        self.assertContains(
            response, "No individual talk timestamps recorded for this meetup."
        )

    def test_meetup_year_404(self):
        url = reverse("meetup_year", kwargs={"year": 1999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestMeetupSitemap(test.TestCase):
    def test_sitemap(self):
        Meetup.objects.create(
            title="September 2026 Monthly Meetup",
            date=date(2026, 9, 24),
            youtube_id="fM-P0ZLY-_U",
        )
        sitemap = MeetupYearSitemap()
        items = sitemap.items()
        self.assertEqual(items, [2026])
        self.assertEqual(sitemap.location(2026), "/meetups/2026/")


class TestYouTubeIngestView(test.TestCase):
    def setUp(self):
        self.url = reverse("youtube_ingest")

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    @override_settings(YOUTUBE_SYNC_SECRET=None)
    def test_post_secret_not_configured(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Sync secret is not configured", response.content.decode())

    @override_settings(YOUTUBE_SYNC_SECRET="super-secret-token")
    def test_post_missing_or_invalid_auth(self):
        # Missing auth header
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

        # Invalid token
        response = self.client.post(
            self.url,
            headers={"Authorization": "Bearer wrong-token"},
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(YOUTUBE_SYNC_SECRET="super-secret-token")
    @mock.patch("pythonsd.views.fetch_and_sync_youtube_feed")
    def test_post_success(self, mock_sync):
        mock_sync.return_value = {
            "created_meetups": 1,
            "updated_meetups": 0,
            "synced_talks": 3,
        }
        response = self.client.post(
            self.url,
            headers={"Authorization": "Bearer super-secret-token"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["created_meetups"], 1)

    @override_settings(YOUTUBE_SYNC_SECRET="super-secret-token")
    @mock.patch("pythonsd.views.fetch_and_sync_youtube_feed")
    def test_post_sync_exception(self, mock_sync):
        mock_sync.side_effect = RuntimeError("Network down")
        response = self.client.post(
            self.url,
            headers={"Authorization": "Bearer super-secret-token"},
        )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["status"], "error")


class TestYouTubeService(test.TestCase):
    def test_parse_meetup_description_with_timestamps(self):
        desc = """
        This is our monthly meetup from September 24, 2026.
        https://www.meetup.com/pythonsd/events/312775789/

        TIMESTAMPS
        00:00 Waiting to start
        04:08 Introductions
        10:12 Jane User - Why Your AI Agent Is Only as Good as Your Data
        19:48 Alex Developer: Variables and objects in Python (30m)
        1:09:47 Sam Coder – Managing Secrets in Python
        1:30:00 Standalone Topic Without Delimiter
        Slides available at github.com/example/slides
        1:45:00 Outro
        """

        talks, meetup_url = parse_meetup_description(desc)
        self.assertEqual(
            meetup_url, "https://www.meetup.com/pythonsd/events/312775789/"
        )
        self.assertEqual(len(talks), 4)

        self.assertEqual(talks[0]["speaker_name"], "Jane User")
        self.assertEqual(
            talks[0]["title"], "Why Your AI Agent Is Only as Good as Your Data"
        )
        self.assertEqual(talks[0]["timestamp_seconds"], 612)
        self.assertEqual(talks[0]["timestamp_label"], "10:12")

        self.assertEqual(talks[1]["speaker_name"], "Alex Developer")
        self.assertEqual(talks[1]["timestamp_seconds"], 1188)

        self.assertEqual(talks[2]["speaker_name"], "Sam Coder")
        self.assertEqual(talks[2]["timestamp_seconds"], 4187)

        self.assertEqual(talks[3]["speaker_name"], "")
        self.assertEqual(talks[3]["title"], "Standalone Topic Without Delimiter")

    def test_parse_meetup_description_without_timestamps(self):
        desc = "Just a short description without any timestamps."
        talks, meetup_url = parse_meetup_description(desc)
        self.assertEqual(talks, [])
        self.assertEqual(meetup_url, "")

    def test_extract_meetup_date(self):
        # Description date takes priority over fallback_date (due to Friday feed publish timing)
        desc1 = "Livestream from September 24, 2026."
        feed_date = date(2026, 9, 25)
        self.assertEqual(
            extract_meetup_date("Meetup", desc1, fallback_date=feed_date),
            date(2026, 9, 24),
        )

        # Fallback to fallback_date if description has no date
        desc_no_date = "Just a description with no date string."
        self.assertEqual(
            extract_meetup_date("Meetup", desc_no_date, fallback_date=feed_date),
            feed_date,
        )

        # Invalid date in description, fallback to title
        desc_bad = "Livestream from Notadate 99, 9999."
        self.assertEqual(
            extract_meetup_date("October 2025 Monthly Meetup", desc_bad),
            date(2025, 10, 1),
        )

        # Title without date, use fallback_date
        fallback = date(2024, 1, 15)
        self.assertEqual(
            extract_meetup_date("Title Without Date", "No date in desc", fallback),
            fallback,
        )

        # Title with invalid month, fallback to today
        self.assertIsInstance(
            extract_meetup_date("BadMonth 2024 Meetup", "No date in desc"),
            date,
        )

        # No dates at all, defaults to today
        today = extract_meetup_date("Random Title", "Random Description")
        self.assertIsInstance(today, date)

    def test_sync_meetup_record(self):
        desc = """
        from September 24, 2026
        TIMESTAMPS
        10:12 Jane User - Talk 1
        """
        meetup, created = sync_meetup_record(
            youtube_id="vid_123",
            title="September 2026 Monthly Meetup",
            description=desc,
        )
        self.assertTrue(created)
        self.assertEqual(meetup.talks.count(), 1)
        self.assertEqual(meetup.date, date(2026, 9, 24))

        # Explicit meetup URL
        meetup_explicit, _ = sync_meetup_record(
            youtube_id="vid_explicit",
            title="Explicit URL Meetup",
            description="No timestamps",
            meetup_url="https://explicit-url.com",
        )
        self.assertEqual(meetup_explicit.meetup_url, "https://explicit-url.com")

        # Update existing record
        updated_desc = """
        from September 24, 2026
        TIMESTAMPS
        10:12 Jane User - Talk 1 Updated
        20:00 Alex Developer - Talk 2
        """
        meetup_updated, created_again = sync_meetup_record(
            youtube_id="vid_123",
            title="September 2026 Monthly Meetup Updated",
            description=updated_desc,
        )
        self.assertFalse(created_again)
        self.assertEqual(meetup_updated.pk, meetup.pk)
        self.assertEqual(meetup_updated.talks.count(), 2)

    @responses.activate
    def test_fetch_and_sync_youtube_feed(self):
        responses.add(
            responses.GET,
            settings.YOUTUBE_FEED_URL,
            body=SAMPLE_RSS_FEED,
            status=200,
            content_type="application/xml",
        )
        stats = fetch_and_sync_youtube_feed()
        self.assertEqual(stats["created_meetups"], 3)
        self.assertEqual(stats["updated_meetups"], 0)
        self.assertEqual(stats["synced_talks"], 1)

        # Run again to verify updated_meetups
        stats_updated = fetch_and_sync_youtube_feed()
        self.assertEqual(stats_updated["created_meetups"], 0)
        self.assertEqual(stats_updated["updated_meetups"], 3)


class TestManagementCommands(test.TestCase):
    @responses.activate
    def test_sync_youtube_command(self):
        responses.add(
            responses.GET,
            settings.YOUTUBE_FEED_URL,
            body=SAMPLE_RSS_FEED,
            status=200,
            content_type="application/xml",
        )
        call_command("sync_youtube")
        self.assertEqual(Meetup.objects.count(), 3)

    def test_import_meetups_json_lines(self):
        line1 = json.dumps(
            {
                "id": "vid_lines_1",
                "title": "August 2026 Monthly Meetup",
                "release_timestamp": 1787882882,
                "description": "from August 27, 2026\nTIMESTAMPS\n05:00 Jane User - Title",
            }
        )
        line2 = json.dumps(
            {
                "id": "vid_lines_2",
                "title": "September 2026 Monthly Meetup",
                "release_timestamp": "2026-09-25T02:04:41+00:00",
                "description": "from September 24, 2026\nTIMESTAMPS\n05:00 Alex Developer - Title",
            }
        )
        line3 = json.dumps(
            {
                "id": "vid_lines_3",
                "title": "October 2026 Monthly Meetup",
                "release_timestamp": "invalid_ts",
                "upload_date": "20261023",
                "description": "TIMESTAMPS\n05:00 Sam Coder - Title",
            }
        )
        line4 = json.dumps(
            {
                "id": "vid_lines_4",
                "title": "November 2026 Monthly Meetup",
                "description": "from November 19, 2026\nTIMESTAMPS\n05:00 Alex Developer - Title",
            }
        )
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(f"{line1}\n\n{line2}\n{line3}\n{line4}\n")
            temp_path = f.name

        try:
            call_command("import_meetups", temp_path)
            m1 = Meetup.objects.get(youtube_id="vid_lines_1")
            m2 = Meetup.objects.get(youtube_id="vid_lines_2")
            m3 = Meetup.objects.get(youtube_id="vid_lines_3")
            m4 = Meetup.objects.get(youtube_id="vid_lines_4")
            self.assertEqual(m1.date, date(2026, 8, 27))
            self.assertEqual(m2.date, date(2026, 9, 24))
            self.assertEqual(m3.date, date(2026, 10, 23))
            self.assertEqual(m4.date, date(2026, 11, 19))
            # Re-import to test updated_count
            call_command("import_meetups", temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_meetups_json_array(self):
        data = [
            {
                "youtube_id": "vid_array_1",
                "title": "July 2026 Monthly Meetup",
                "upload_date": "invalid",
                "description": "from July 23, 2026\nTIMESTAMPS\n05:00 Jane User - Title",
            }
        ]
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(json.dumps(data))
            temp_path = f.name

        try:
            call_command("import_meetups", temp_path)
            self.assertEqual(Meetup.objects.filter(youtube_id="vid_array_1").count(), 1)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_meetups_missing_file(self):
        with self.assertRaises(CommandError):
            call_command("import_meetups", "/path/to/nonexistent_file.json")
