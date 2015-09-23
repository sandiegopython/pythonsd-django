from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.views import generic

from homepage.views import home_view

urlpatterns = [
    url(r'^$', home_view, name='home'),
    url(r'^chat-room.html$', generic.TemplateView.as_view(template_name='pythonsd/pages/chat-room.html'), name='chat-room'),
    url(r'^code-of-conduct.html$', generic.TemplateView.as_view(template_name='pythonsd/pages/code-of-conduct.html'), name='code-of-conduct'),
    url(r'^getting-started.html$', generic.TemplateView.as_view(template_name='pythonsd/pages/getting-started.html'), name='getting-started'),
    url(r'^job-posting-guidelines.html$', generic.TemplateView.as_view(template_name='pythonsd/pages/job-posting.html'), name='job-posting'),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns.extend(static.static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    ))
