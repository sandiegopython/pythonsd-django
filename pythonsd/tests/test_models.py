from datetime import date

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile

from ..admin import MeetupAdmin
from ..admin import SponsorAdmin
from ..models import Meetup
from ..models import Organizer
from ..models import Sponsor
from ..models import Talk


# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class TestOrganizer(test.TestCase):
    def setUp(self):
        self.org1 = Organizer(
            name="First organizer",
            meetup_url="http://example.com/meetup",
            linkedin_url="http://example.com/linkedin",
            photo=SimpleUploadedFile(
                name="test.png", content=ONE_PIXEL_PNG_BYTES, content_type="image/png"
            ),
        )
        self.org1.save()

        self.org2 = Organizer(
            name="Second organizer",
            meetup_url="http://example.com/meetup",
            photo=SimpleUploadedFile(
                name="test.png", content=ONE_PIXEL_PNG_BYTES, content_type="image/png"
            ),
        )
        self.org2.save()

    def test_str(self):
        self.assertEqual(str(self.org1), self.org1.name)


class TestSponsor(test.TestCase):
    def setUp(self):
        self.sponsor = Sponsor(
            name="First Sponsor",
            website_url="http://example.com/",
            logo=SimpleUploadedFile(
                name="test.png", content=ONE_PIXEL_PNG_BYTES, content_type="image/png"
            ),
        )
        self.sponsor.save()

    def test_str(self):
        self.assertEqual(str(self.sponsor), self.sponsor.name)

    def test_sponsor_admin(self):
        """Test the sponsor admin - displaying the logo."""
        admin = SponsorAdmin(Sponsor, None)

        self.assertEqual(admin.display_logo(None), "")
        self.assertIn(self.sponsor.logo.url, admin.display_logo(self.sponsor))


class TestMeetup(test.TestCase):
    def setUp(self):
        self.meetup = Meetup.objects.create(
            title="September 2026 Monthly Meetup",
            date=date(2026, 9, 24),
            youtube_id="fM-P0ZLY-_U",
            meetup_url="https://www.meetup.com/pythonsd/events/312775789/",
        )
        self.talk = Talk.objects.create(
            meetup=self.meetup,
            speaker_name="Jane User",
            title="Classes in Python",
            timestamp_seconds=1468,
            timestamp_label="24:28",
            order=0,
        )

    def test_str(self):
        self.assertEqual(str(self.meetup), self.meetup.title)

    def test_youtube_url(self):
        self.assertEqual(
            self.meetup.youtube_url,
            "https://www.youtube.com/watch?v=fM-P0ZLY-_U",
        )

    def test_meetup_admin(self):
        admin = MeetupAdmin(Meetup, None)
        request = test.RequestFactory().get("/")
        qs = admin.get_queryset(request)
        annotated_meetup = qs.get(pk=self.meetup.pk)
        with self.assertNumQueries(0):
            self.assertEqual(admin.talk_count(annotated_meetup), 1)
        self.assertEqual(admin.talk_count(self.meetup), 1)

        self.assertIn(
            'href="https://www.youtube.com/watch?v=fM-P0ZLY-_U"',
            admin.youtube_link(self.meetup),
        )
        self.assertEqual(admin.youtube_link(None), "")
        self.assertEqual(admin.youtube_link(Meetup()), "")


class TestTalk(test.TestCase):
    def setUp(self):
        self.meetup = Meetup.objects.create(
            title="September 2026 Monthly Meetup",
            date=date(2026, 9, 24),
            youtube_id="fM-P0ZLY-_U",
        )

    def test_str_with_speaker(self):
        talk = Talk(
            meetup=self.meetup,
            speaker_name="Jane User",
            title="Classes in Python",
            timestamp_seconds=1468,
            timestamp_label="24:28",
        )
        self.assertEqual(str(talk), "Jane User - Classes in Python")

    def test_str_without_speaker(self):
        talk = Talk(
            meetup=self.meetup,
            speaker_name="",
            title="Open Discussions",
            timestamp_seconds=300,
            timestamp_label="05:00",
        )
        self.assertEqual(str(talk), "Open Discussions")

    def test_youtube_url(self):
        talk = Talk(
            meetup=self.meetup,
            speaker_name="Jane User",
            title="Classes in Python",
            timestamp_seconds=1468,
            timestamp_label="24:28",
        )
        self.assertEqual(
            talk.youtube_url,
            "https://www.youtube.com/watch?v=fM-P0ZLY-_U&t=1468s",
        )
