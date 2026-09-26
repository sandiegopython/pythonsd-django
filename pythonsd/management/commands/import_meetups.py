"""
Import historical meetups further back than the YouTube RSS supports.

This will typically be run one-time rather than an ongoing basis.

To generate the JSON file from YouTube:

  > uvx yt-dlp -j --skip-download "https://www.youtube.com/@sandiegopython/streams" \
     | jq -c '{id: .id, title: .title, release_timestamp: .release_timestamp, description: .description}' > meetups_clean.json
"""

import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone

from pythonsd.youtube import extract_meetup_date
from pythonsd.youtube import sync_meetup_record


class Command(BaseCommand):
    help = "Import past meetups from a JSON file (via `yt-dlp`)."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        path = Path(options["file_path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        records = []
        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                records = json.loads(content)
            else:
                for line in content.splitlines():
                    if line.strip():
                        records.append(json.loads(line))

        created_count = 0
        updated_count = 0
        talks_count = 0

        for item in records:
            video_id = item.get("id") or item.get("youtube_id")
            title = item.get("title", "")
            description = item.get("description", "")
            event_date = None
            release_ts = item.get("release_timestamp") or item.get("timestamp")
            if release_ts:
                try:
                    current_tz = timezone.get_current_timezone()
                    if isinstance(release_ts, (int, float)):
                        event_date = datetime.fromtimestamp(
                            release_ts, tz=current_tz
                        ).date()
                    else:
                        event_date = (
                            datetime.fromisoformat(str(release_ts))
                            .astimezone(current_tz)
                            .date()
                        )
                except (ValueError, OSError):
                    pass

            if event_date is None:
                upload_date_str = item.get("upload_date")
                fallback_date = None
                if upload_date_str:
                    try:
                        fallback_date = datetime.strptime(
                            str(upload_date_str), "%Y%m%d"
                        ).date()
                    except ValueError:
                        pass
                event_date = extract_meetup_date(title, description, fallback_date)

            meetup, created = sync_meetup_record(
                youtube_id=video_id,
                title=title,
                description=description,
                event_date=event_date,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
            talks_count += meetup.talks.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created_count} created, {updated_count} updated, "
                f"{talks_count} talks total across {len(records)} meetups."
            )
        )
