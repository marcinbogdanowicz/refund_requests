from apps.core.models import UserProfile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    prefix = "user"

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class UserProfileCreationForm(forms.ModelForm):
    prefix = "profile"

    class Meta:
        model = UserProfile
        fields = ("phone_number",)
