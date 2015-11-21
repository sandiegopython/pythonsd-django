from datetime import datetime
import json
import urllib

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import models

REDIRECT_URI = 'http://127.0.0.1:8000/raffle'
MEETUP_API_URL = 'https://api.meetup.com'

@login_required
def raffle_view(request):
    meetup_auth_code = request.GET.get('code')
    if meetup_auth_code:
        auth_response = requests.post('https://secure.meetup.com/oauth2/access', data={
            'client_id': settings.MEETUP_KEY,
            'client_secret': settings.MEETUP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'code': meetup_auth_code,
        })
        auth_response.raise_for_status()
        auth_response_data = auth_response.json()
        models.MeetupKey.objects.create(
            user=request.user,
            access_token=auth_response_data['access_token'],
            refresh_token=auth_response_data['refresh_token'],
        )
    try:
        meetup_key = models.MeetupKey.objects.get(user=request.user)
    except models.MeetupKey.DoesNotExist:
        meetup_authorize_url = 'https://secure.meetup.com/oauth2/authorize?{}'.format(urllib.urlencode({
            'client_id': settings.MEETUP_KEY,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
        }))
        return render(request, template_name='raffle/auth.html', context={'auth_link': meetup_authorize_url})
    refresh_response = requests.post('https://secure.meetup.com/oauth2/access', data={
        'client_id': settings.MEETUP_KEY,
        'client_secret': settings.MEETUP_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': meetup_key.refresh_token,
    })
    refresh_response.raise_for_status()
    meetup_key.access_token = refresh_response.json()['access_token']
    events = requests.get(MEETUP_API_URL + '/2/events', params={
        'sign': True,
        'group_urlname': 'pythonsd',
        'status': 'upcoming,past',
        'time': '-1w,1w'
    }).json()['results']
    for event in events:
        event['time'] = datetime.fromtimestamp(event['time'] / 1000).isoformat()
    for event in events:
        attendance_resp = requests.get(MEETUP_API_URL + '/2/rsvps', params={
            'event_id': event['id'],
            'rsvp': 'yes',
            'page': 200,
            'sign': True,
            'access_token': meetup_key.access_token,
        })
        attendance_resp.raise_for_status()
        event['attendees'] = attendance_resp.json()['results']
    return render(request, template_name='raffle/raffle.html', context={
        'events': json.dumps(events),
    })

