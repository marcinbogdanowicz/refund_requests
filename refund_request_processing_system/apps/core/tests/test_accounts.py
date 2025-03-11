import re
from contextlib import suppress
from unittest.mock import patch
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.core.forms import (
    BootstrapAuthenticationForm,
    BootstrapPasswordResetForm,
    BootstrapSetPasswordForm,
    CustomUserCreationForm,
    UserProfileCreationForm,
)
from apps.core.models import UserProfile
from apps.core.tests.helpers import ExpectedException


class SignUpViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.signup_url = reverse("signup")
        cls.valid_data = {
            "user-username": "testuser",
            "user-email": "test@example.com",
            "user-password1": "testpass123",
            "user-password2": "testpass123",
            "user-first_name": "Test",
            "user-last_name": "User",
            "profile-phone_number": "+48123456789",
        }

    def test_signup_page_loads_correctly(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertIsInstance(response.context["user_form"], CustomUserCreationForm)
        self.assertIsInstance(response.context["profile_form"], UserProfileCreationForm)

    def test_successful_signup(self):
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)

        user = User.objects.first()
        self.assertEqual(user.username, self.valid_data["user-username"])
        self.assertEqual(user.email, self.valid_data["user-email"])
        self.assertTrue(user.check_password(self.valid_data["user-password1"]))

        profile = user.userprofile
        self.assertEqual(profile.phone_number, self.valid_data["profile-phone_number"])

    def test_invalid_signup(self):
        response = self.client.post(
            self.signup_url, self.valid_data | {"user-password2": "wrongpass"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["user_form"],
            "password2",
            "The two password fields didn’t match.",
        )
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(UserProfile.objects.count(), 0)

    @patch("apps.core.models.UserProfile.save", side_effect=ExpectedException)
    def test_transaction_rollback(self, _):
        with suppress(ExpectedException):
            self.client.post(self.signup_url, self.valid_data)

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(UserProfile.objects.count(), 0)


class LoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.login_url = reverse("login")
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        cls.valid_data = {"username": "testuser", "password": "testpass123"}

    def test_login_page_loads_correctly(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertContains(response, "Login")
        self.assertContains(response, reverse("signup"))
        self.assertContains(response, reverse("password_reset"))

    def test_successful_login(self):
        response = self.client.post(self.login_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("refund_list"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_credentials(self):
        invalid_data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(self.login_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_page_uses_bootstrap_form(self):
        response = self.client.get(self.login_url)
        self.assertIn('class="form-control"', str(response.content))
        self.assertIsInstance(response.context["form"], BootstrapAuthenticationForm)


class PasswordResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )
        cls.password_reset_url = reverse("password_reset")
        cls.password_reset_done_url = reverse("password_reset_done")

    def test_password_reset_page_loads_correctly(self):
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_generic.html")
        self.assertContains(response, "Reset password")
        self.assertIsInstance(response.context["form"], BootstrapPasswordResetForm)

    def test_password_reset_sends_email(self):
        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.client.post(
                self.password_reset_url, {"email": "test@example.com"}
            )
            self.assertRedirects(response, self.password_reset_done_url)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["test@example.com"])

    def test_password_reset_complete_workflow(self):
        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            # Request a reset link
            self.client.post(self.password_reset_url, {"email": "test@example.com"})
            email_body = mail.outbox[0].body
            url_match = re.search(r"http://[^\s]+", email_body)
            reset_url = url_match.group()

            path = urlparse(reset_url).path
            uidb64 = path.split("/")[-3]

            # Open the link - should redirect to set password page
            response = self.client.get(reset_url)
            set_password_url = reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uidb64, "token": "set-password"},
            )
            self.assertRedirects(response, set_password_url)

            # Verify set password page is customized
            response = self.client.get(set_password_url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, "registration/password_reset_generic.html"
            )
            self.assertIsInstance(response.context["form"], BootstrapSetPasswordForm)

            # Set new password
            new_password = "newpass123"
            response = self.client.post(
                set_password_url,
                {"new_password1": new_password, "new_password2": new_password},
            )
            self.assertRedirects(response, reverse("password_reset_complete"))

            self.assertTrue(
                self.client.login(username="testuser", password=new_password)
            )
