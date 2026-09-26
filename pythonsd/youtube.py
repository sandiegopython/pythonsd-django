import logging
import re
from datetime import date
from datetime import datetime

import requests
from defusedxml import ElementTree
from django.conf import settings
from django.utils import timezone

from .models import Meetup
from .models import Talk


log = logging.getLogger(__name__)

# Parses timestamps like "1:23:45" or "19:87"
TIMESTAMP_RE = re.compile(r"^(?:(\d+):)?([0-5]?\d):([0-5]\d)\s+(.+)$")

# Ignore these
NON_TALK_KEYWORDS = (
    "waiting to start",
    "starting soon",
    "introductions",
    "outro",
    "wrap up",
    "wrapup",
    "closing remarks",
    "promo",
    "break",
    "announcements",
    "pre show",
)

# Parse the meetup date written by organizers in the video description.
# The livestreams are usually recorded on Thursday evenings
# but the published date by YouTube shows Friday (even after adjusting for TZ),
# so the description date is the most accurate source for the actual meetup date.
# I believe the incorrect published date in the RSS feed is due to YT's processing
# of the livestream which happens over hours
DATE_FROM_RE = re.compile(r"from ([A-Za-z]+ \d{1,2}, \d{4})", re.IGNORECASE)

# Grab the meetup URL from the YouTube description too
MEETUP_URL_RE = re.compile(
    r"https?://(?:www\.)?meetup\.com/pythonsd/events/[^\s/]+/?",
    re.IGNORECASE,
)


def parse_meetup_description(description: str) -> tuple[list[dict], str]:
    """Parse talk timestamps and Meetup event URL from a YouTube description."""
    talks = []
    meetup_url = ""

    url_match = MEETUP_URL_RE.search(description)
    if url_match:
        meetup_url = url_match.group(0)

    in_timestamps = False
    order = 0

    for line in description.splitlines():
        line = line.strip()
        if re.search(r"timestamps?", line, re.IGNORECASE):
            in_timestamps = True
            continue

        if not in_timestamps or not line:
            continue

        match = TIMESTAMP_RE.match(line)
        if not match:
            continue

        # Parse the H/M/S from the timestamp - used for display only
        hours, minutes, seconds, raw_title = match.groups()
        total_seconds = (int(hours or 0) * 3600) + (int(minutes) * 60) + int(seconds)

        if any(keyword in raw_title.lower() for keyword in NON_TALK_KEYWORDS):
            continue

        # Split on standard delimiters: " - ", ": ", " – ", " — "
        parts = re.split(r"(?:\s+[-–—]\s+|:\s+)", raw_title, maxsplit=1)
        if len(parts) > 1:
            speaker_name, title = parts[0].strip(), parts[1].strip()

        else:
            speaker_name, title = "", raw_title.strip()

        label = f"{hours}:{minutes}:{seconds}" if hours else f"{minutes}:{seconds}"

        talks.append(
            {
                "timestamp_seconds": total_seconds,
                "timestamp_label": label,
                "speaker_name": speaker_name,
                "title": title,
                "order": order,
            }
        )
        order += 1

    return talks, meetup_url


def extract_meetup_date(
    title: str,
    description: str,
    fallback_date: date | None = None,
) -> date:
    """
    Extract meetup date from description, falling back to feed published date or title.

    The description date is prioritized because organizers explicitly record the
    Thursday evening meetup date, whereas YouTube publishes livestream archives
    on Friday morning.
    """
    date_match = DATE_FROM_RE.search(description)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), "%B %d, %Y").date()
        except ValueError:
            pass

    if fallback_date:
        return fallback_date

    # Try parsing Month YYYY from title (e.g. "September 2026 Monthly Meetup")
    title_match = re.search(r"([A-Za-z]+ \d{4})", title)
    if title_match:
        try:
            parsed = datetime.strptime(title_match.group(1), "%B %Y").date()
            return parsed
        except ValueError:
            pass

    return timezone.localdate()


def sync_meetup_record(
    youtube_id: str,
    title: str,
    description: str,
    event_date: date | None = None,
    meetup_url: str = "",
) -> tuple[Meetup, bool]:
    """Create or update a Meetup and its associated talks."""
    talks_data, parsed_meetup_url = parse_meetup_description(description)
    if not meetup_url:
        meetup_url = parsed_meetup_url

    if event_date is None:
        event_date = extract_meetup_date(title, description)

    # Treat the YouTube ID as the unique ID
    # This field has a unique key on the model
    meetup, created = Meetup.objects.update_or_create(
        youtube_id=youtube_id,
        defaults={
            "title": title,
            "date": event_date,
            "meetup_url": meetup_url,
            "description": description,
        },
    )

    # Recreate talks for this meetup
    meetup.talks.all().delete()
    talk_objects = [
        Talk(
            meetup=meetup,
            speaker_name=talk["speaker_name"],
            title=talk["title"],
            timestamp_seconds=talk["timestamp_seconds"],
            timestamp_label=talk["timestamp_label"],
            order=talk["order"],
        )
        for talk in talks_data
    ]
    Talk.objects.bulk_create(talk_objects)

    return meetup, created


def fetch_and_sync_youtube_feed() -> dict:
    """Fetch the latest YouTube Atom RSS feed and sync meetups."""
    log.info("Fetching YouTube RSS feed from %s", settings.YOUTUBE_FEED_URL)
    resp = requests.get(settings.YOUTUBE_FEED_URL, timeout=10)
    resp.raise_for_status()

    dom = ElementTree.fromstring(resp.content)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }

    created_count = 0
    updated_count = 0
    synced_talks = 0

    for entry in dom.findall("atom:entry", ns):
        video_id_elem = entry.find("yt:videoId", ns)
        title_elem = entry.find("atom:title", ns)
        media_group = entry.find("media:group", ns)

        if video_id_elem is None or title_elem is None:
            continue

        video_id = video_id_elem.text
        title = title_elem.text

        description = ""
        if media_group is not None:
            desc_elem = media_group.find("media:description", ns)
            if desc_elem is not None and desc_elem.text:
                description = desc_elem.text

        # Extract published date for fallback
        published_elem = entry.find("atom:published", ns)
        fallback_date = None
        if published_elem is not None and published_elem.text:
            try:
                published_dt = datetime.fromisoformat(published_elem.text)
                fallback_date = published_dt.astimezone(
                    timezone.get_current_timezone()
                ).date()
            except ValueError:
                pass

        event_date = extract_meetup_date(
            title, description, fallback_date=fallback_date
        )

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
        synced_talks += meetup.talks.count()

    return {
        "created_meetups": created_count,
        "updated_meetups": updated_count,
        "synced_talks": synced_talks,
    }
