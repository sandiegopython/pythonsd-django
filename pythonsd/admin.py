from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Meetup
from .models import Organizer
from .models import Sponsor
from .models import Talk


admin.site.register(Organizer)


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    # This is the width used in the admin interface
    MAX_IMAGE_WIDTH = 100

    list_display = (
        "display_logo",
        "name",
        "active",
        "order",
    )
    list_filter = ("active",)
    readonly_fields = ("display_logo",)
    ordering = ("order",)

    @admin.display(description="Logo")
    def display_logo(self, obj):
        """Display the sponsor logo in the admin interface."""
        if not obj:
            return ""

        return format_html(
            '<img src="{}" style="max-width: {}px" />',
            obj.logo.url,
            self.MAX_IMAGE_WIDTH,
        )


class TalkInline(admin.TabularInline):
    model = Talk
    extra = 0
    fields = ("order", "timestamp_label", "timestamp_seconds", "speaker_name", "title")


@admin.register(Meetup)
class MeetupAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "date",
        "youtube_id",
        "youtube_link",
        "meetup_url",
        "description",
    )
    readonly_fields = ("youtube_link",)
    list_display = ("title", "date", "youtube_id", "talk_count")
    list_filter = ("date",)
    search_fields = ("title", "description", "talks__title", "talks__speaker_name")
    inlines = [TalkInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(talk_count=Count("talks"))

    @admin.display(description="Talks", ordering="talk_count")
    def talk_count(self, obj):
        # Avoid the N+1 query
        if hasattr(obj, "talk_count"):
            return obj.talk_count
        return obj.talks.count()

    @admin.display(description="YouTube Link")
    def youtube_link(self, obj):
        if not obj or not obj.youtube_id:
            return ""
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            obj.youtube_url,
            obj.youtube_url,
        )
