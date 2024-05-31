from django import test
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Organizer


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
