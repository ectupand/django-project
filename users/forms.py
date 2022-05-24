from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from users.models import Follow

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

class FollowForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Follow
        fields = ("author", "user")



