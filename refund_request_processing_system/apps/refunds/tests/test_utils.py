from unittest.mock import patch

from django.test import TestCase

from apps.core.mixins import FlushRedisDBTestMixin
from apps.refunds.utils import IBANValidator


class IBANValidatorTests(FlushRedisDBTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.valid_iban = 'DE89370400440532013000'
        self.validator = IBANValidator(self.valid_iban, 'DE')

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_valid_iban_no_error(self, mock_validate):
        mock_validate.return_value = {'valid': True, 'country': 'DE'}
        self.assertIsNone(self.validator.get_error())

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_invalid_iban_returns_error(self, mock_validate):
        mock_validate.return_value = {'valid': False}
        self.assertEqual(
            self.validator.get_error(), 'Provided number is not a valid IBAN.'
        )

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_wrong_country_returns_error(self, mock_validate):
        mock_validate.return_value = {'valid': True, 'country': 'FR'}
        self.assertEqual(
            self.validator.get_error(),
            'Provided IBAN number comes from FR, while DE was provided.',
        )

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_service_unavailable_raises_error(self, mock_validate):
        mock_validate.return_value = None
        with self.assertRaisesRegex(
            RuntimeError, 'Validation service is unavailable.'
        ):
            self.validator.get_error()

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_result_is_cached(self, mock_validate):
        mock_validate.return_value = {'valid': True, 'country': 'DE'}

        first_result = self.validator.get_error()
        mock_validate.return_value = {'valid': False}
        second_result = self.validator.get_error()

        self.assertEqual(first_result, second_result)
        mock_validate.assert_called_once()

    def test_cache_key_generation(self):
        validator1 = IBANValidator('iban1', 'DE')
        validator2 = IBANValidator('iban1', 'DE')
        validator3 = IBANValidator('iban1', 'FR')

        self.assertEqual(validator1.cache_key, validator2.cache_key)
        self.assertNotEqual(validator1.cache_key, validator3.cache_key)

    @patch('django.core.cache.cache.set')
    def test_cache_valid_iban(self, mock_cache_set):
        self.validator.cache_valid_iban()
        mock_cache_set.assert_called_once_with(self.validator.cache_key, None)

    def test_country_case_insensitive(self):
        validator = IBANValidator(self.valid_iban, 'de')

        with patch(
            'apps.refunds.utils.APINinjasClient.validate_iban'
        ) as mock_validate:
            mock_validate.return_value = {'valid': True, 'country': 'DE'}
            self.assertIsNone(validator.get_error())
