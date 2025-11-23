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

    # For production, store the image in Cloud Storage (S3, R2, Appwrite, etc.)
    photo = models.ImageField(
        upload_to="organizers/",
        help_text="Recommended size of 400*400px or larger square",
    )

    def __str__(self):
        return self.name


class Sponsor(models.Model):
    """Meetup sponsors - displayed on the home page page."""

    name = models.CharField(max_length=255)
    website_url = models.URLField(
        max_length=1024,
        blank=True,
        default="",
    )
    description = models.TextField(blank=True, default="")
    logo = models.ImageField(
        upload_to="sponsors/",
        help_text="Recommended size of 300*300px or larger square",
    )
    active = models.BooleanField(
        default=True,
        help_text="Set to False to hide this sponsor from the sponsors page",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Sponsors are displayed in ascending order of this value",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("order",)
