from django.shortcuts import render

from sponsors.models import Sponsor


def home_view(request):
    return render(request, template_name='homepage/index.html', context={
        'sponsors': Sponsor.objects.all(),
    })
