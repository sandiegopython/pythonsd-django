from django import test

from ..models import Organizer


class TestOrganizer(test.TestCase):
    def setUp(self):
        self.org1 = Organizer(
            name="First organizer",
            meetup_url="http://example.com/meetup",
            linkedin_url="http://example.com/linkedin",
        )
        self.org1.save()

        self.org2 = Organizer(
            name="Second organizer", meetup_url="http://example.com/meetup"
        )
        self.org2.save()

    def test_str(self):
        self.assertEqual(str(self.org1), self.org1.name)
