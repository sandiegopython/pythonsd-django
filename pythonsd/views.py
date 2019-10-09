from datetime import datetime
import logging

from django.core.cache import cache
from django.http import JsonResponse
from django.views.generic import TemplateView
import pytz
import requests


log = logging.getLogger(__file__)


class MeetupWidget(TemplateView):

    """
    Creates an HTML meetup widget that can be embedded onto the site with an iframe

    - Handles caching requests to meetup so we don't get rate limited
    - Allows fetching JSON of events
    """

    cache_duration = 60 * 15
    cache_key = 'pythonsd.views.MeetupWidget'
    http_method_names = ['get', 'head', 'options']
    template_name = 'pythonsd/meetup-widget.html'

    def get(self, request, *args, **kwargs):
        format = kwargs.get('format')

        if format == 'json':
            response = JsonResponse(self.get_upcoming_events(), safe=False)
        else:
            response = super().get(self, request, *args, **kwargs)

        response['Access-Control-Allow-Origin'] = '*'

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.get_upcoming_events()
        return context

    def get_upcoming_events(self):
        events = cache.get(self.cache_key)
        if events:
            log.debug('Using Meetup.com events from cache')
            return events

        log.debug('Requesting upcoming events from Meetup.com')

        # https://www.meetup.com/meetup_api/docs/:urlname/events/
        try:
            resp = requests.get(
                'https://api.meetup.com/pythonsd/events',
                params={'photo-host': 'public', 'page': '3'},
                timeout=5,
            )
        except Exception:
            return []
        if resp.ok:
            # Transform from meetup's API format into our format
            events = [
                {
                    'link': e['link'],
                    'name': e['name'],
                    # Always show time in local San Diego time
                    'datetime': datetime.utcfromtimestamp(e['time'] // 1000).replace(
                        tzinfo=pytz.utc).astimezone(pytz.timezone('America/Los_Angeles')),
                    'venue': e['venue']['name'] if 'venue' in e else None,
                }
                for e in resp.json()
            ]
            cache.set(self.cache_key, events, self.cache_duration)
            return events

        return []
