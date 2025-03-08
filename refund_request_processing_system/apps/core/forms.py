from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from apps.core.mixins import BootstrapFormMixin
from apps.core.models import UserProfile


class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
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


class UserProfileCreationForm(BootstrapFormMixin, forms.ModelForm):
    prefix = "profile"

    class Meta:
        model = UserProfile
        fields = ("phone_number",)


class BootstrapPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    pass


class BootstrapAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    pass


class BootstrapSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass
