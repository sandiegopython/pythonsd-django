from django.conf import settings
from django.db import models


class MeetupKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
