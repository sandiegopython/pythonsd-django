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


class Meetup(models.Model):
    """
    Periodic meetup with a link to YouTube and meetup.com.

    For SD Python, we stream our monthly meetup to YouTube live.
    Records for this model are fetched from the YouTube RSS feed
    and the video descriptions are parsed into talks.
    """

    title = models.CharField(max_length=255)
    date = models.DateField(db_index=True)
    youtube_id = models.CharField(max_length=32, unique=True)
    meetup_url = models.URLField(max_length=1024, blank=True, default="")
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return self.title

    @property
    def youtube_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"


class Talk(models.Model):
    """An individual presentation or segment within a meetup."""

    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name="talks")
    speaker_name = models.CharField(max_length=255, blank=True, default="")
    title = models.CharField(max_length=255)
    timestamp_seconds = models.PositiveIntegerField(help_text="Start time in seconds")
    timestamp_label = models.CharField(
        max_length=16,
        help_text="Timestamp as displayed on YouTube (e.g. 10:12)",
    )
    # Probably unnecessary given we could order by `timestamp_seconds` but more explicit
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "timestamp_seconds")

    def __str__(self):
        if self.speaker_name:
            return f"{self.speaker_name} - {self.title}"
        return self.title

    @property
    def youtube_url(self):
        return (
            f"https://www.youtube.com/watch?v={self.meetup.youtube_id}"
            f"&t={self.timestamp_seconds}s"
        )
