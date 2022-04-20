from django.contrib import admin
from django.urls import path, include
from . import settings
import debug_toolbar
from django.contrib.flatpages import views

urlpatterns = [
    path("about/", include('django.contrib.flatpages.urls')),
    path("", include("posts.urls")),
    path("auth/", include("Users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += [
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
]

