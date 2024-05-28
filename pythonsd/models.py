from django.db import models


class Organizer(models.Model):
    name = models.CharField(max_length=255)
    meetup_url = models.CharField(max_length=255)
    linkedin_url = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
