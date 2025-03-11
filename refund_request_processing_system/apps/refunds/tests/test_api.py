from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.mixins import ClearCacheTestMixin


class ValidateIBANViewTests(ClearCacheTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        cls.validate_url = reverse('validate_iban')
        cls.valid_data = {'iban': 'DE89370400440532013000', 'country': 'DE'}

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_login_required(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.validate_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.refunds.utils.IBANValidator.get_error')
    def test_valid_iban_returns_no_error(self, mock_get_error):
        mock_get_error.return_value = None
        response = self.client.post(self.validate_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'error': None})
        mock_get_error.assert_called_once()

    @patch('apps.refunds.utils.IBANValidator.get_error')
    def test_invalid_iban_returns_error(self, mock_get_error):
        mock_get_error.return_value = 'Provided number is not a valid IBAN.'
        response = self.client.post(self.validate_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {'error': 'Provided number is not a valid IBAN.'}
        )

    @patch('apps.refunds.utils.IBANValidator.get_error')
    def test_service_unavailable_returns_400(self, mock_get_error):
        mock_get_error.side_effect = RuntimeError(
            'Validation service is unavailable.'
        )
        response = self.client.post(self.validate_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'error': 'Validation service is unavailable.'}
        )

    def test_invalid_payload_returns_400(self):
        response = self.client.post(self.validate_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('iban', data)
        self.assertIn('country', data)
