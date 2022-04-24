from django.contrib import admin
from django.urls import path, include

from posts import views
import debug_toolbar
from django.contrib.flatpages import views as vws


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

