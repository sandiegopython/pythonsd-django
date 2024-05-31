from django.db import models


class Organizer(models.Model):
    """Meetup organizers - displayed on the organizers page."""

    name = models.CharField(max_length=255)
    meetup_url = models.URLField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True)
    active = models.BooleanField(
        default=True,
        help_text="Set to False to hide this organizer from the organizers page",
    )

    # For production, store the image in Cloud Storage (S3, Appwrite, etc.)
    photo = models.ImageField(
        upload_to="organizers/",
        help_text="Recommended size of 400*400px or larger square",
    )

    def __str__(self):
        return self.name
