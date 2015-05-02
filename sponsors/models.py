from django.db import models


class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='sponsors', null=True, blank=True)
    link = models.URLField(null=True, blank=True)