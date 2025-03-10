from unittest.mock import patch

import requests
import responses
from django.conf import settings
from django.test import TestCase, override_settings

from apps.refunds.clients import APINinjasClient


@override_settings(
    API_NINJAS_IBAN_VALIDATION_URL='http://mocked-api-ninjas.com/iban/validate',
    API_NINJAS_API_KEY='mock-api-key',
)
class APINinjasClientTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_client = APINinjasClient()
        cls.valid_iban = 'DE89370400440532013000'

    def test_headers_contain_api_key(self):
        headers = self.api_client.headers
        self.assertEqual(headers['X-Api-Key'], settings.API_NINJAS_API_KEY)

    @responses.activate
    def test_validate_iban_success(self):
        responses.add(
            responses.GET,
            f'{settings.API_NINJAS_IBAN_VALIDATION_URL}?iban={self.valid_iban}',
            json={'valid': True, 'country': 'DE'},
            status=200,
        )

        response = self.api_client.validate_iban(self.valid_iban)

        self.assertEqual(response['valid'], True)
        self.assertEqual(response['country'], 'DE')

    @responses.activate
    def test_validate_iban_error_400(self):
        responses.add(
            responses.GET,
            f'{settings.API_NINJAS_IBAN_VALIDATION_URL}?iban={self.valid_iban}',
            json={'error': 'Invalid Request'},
            status=400,
        )

        with self.assertLogs('django', level='ERROR') as logs:
            response = self.api_client.validate_iban(self.valid_iban)

        self.assertIsNone(response)
        self.assertIn('Invalid Request', logs.output[0])

    @responses.activate
    def test_invalid_json_response(self):
        responses.add(
            responses.GET,
            f'{settings.API_NINJAS_IBAN_VALIDATION_URL}?iban={self.valid_iban}',
            body='Invalid JSON',
            status=200,
        )

        with self.assertLogs('django', level='ERROR') as logs:
            response = self.api_client.validate_iban(self.valid_iban)

        self.assertIsNone(response)
        self.assertIn('Error parsing response', logs.output[0])

    @patch('requests.request')
    def test_connection_error(self, mock_request):
        mock_request.side_effect = requests.exceptions.ConnectionError(
            'mock connection error'
        )

        with self.assertLogs('django', level='ERROR') as logs:
            response = self.api_client.validate_iban(self.valid_iban)

        self.assertIsNone(response)
        self.assertIn('mock connection error', logs.output[0])
