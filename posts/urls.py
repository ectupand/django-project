from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>", views.group_posts, name="group_posts"),
    path("posts/new/", views.new_post, name="new_post")
]