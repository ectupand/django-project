from django.contrib import admin
from django.urls import path, include
from . import settings

urlpatterns = [
    path("", include("posts.urls")),
    path("auth/", include("Users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
]

