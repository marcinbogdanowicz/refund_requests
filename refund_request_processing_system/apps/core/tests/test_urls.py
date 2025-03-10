from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.tests.helpers import ExpectedException


class URLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123',
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_home_url(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refund_list'))

    @override_settings(DEBUG=False)
    def test_404_error_handler(self):
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

    @override_settings(DEBUG=False)
    @patch(
        'apps.core.views.CustomUserCreationForm.__init__',
        side_effect=ExpectedException,
    )
    def test_500_error_handler(self, _):
        self.client.raise_request_exception = False
        response = self.client.post(reverse('signup'))

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'errors/500.html')
