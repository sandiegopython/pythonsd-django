from django.contrib import admin
from django.utils.html import format_html

from .models import Organizer
from .models import Sponsor


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
