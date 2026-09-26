from django.core.management.base import BaseCommand

from pythonsd.youtube import fetch_and_sync_youtube_feed


class Command(BaseCommand):
    help = "Sync recent meetups and talks from the YouTube channel RSS feed."

    def handle(self, *args, **options):
        self.stdout.write("Fetching and syncing YouTube meetups...")
        stats = fetch_and_sync_youtube_feed()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully synced: {stats['created_meetups']} created, "
                f"{stats['updated_meetups']} updated, "
                f"{stats['synced_talks']} talks total."
            )
        )
