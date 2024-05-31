from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf.urls.static import static


urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", include("pythonsd.urls")),
]


if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [path("__debug__", include(debug_toolbar.urls))] + urlpatterns

    # We can't use `settings.MEDIA_URL` as the pattern since MEDIA_URL may be fully qualified
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
