from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts import views
import debug_toolbar
from django.contrib.flatpages import views as vws
from django.conf.urls import handler404, handler500

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("about/", include('django.contrib.flatpages.urls')),
    path("", include("posts.urls")),

    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += [
    path('terms/', vws.flatpage, {'url': '/terms/'}, name='terms'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)