from django.db import models


class Organizer(models.Model):
    """Meetup organizers - displayed on the organizers page."""

    name = models.CharField(max_length=255)
    meetup_url = models.URLField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
