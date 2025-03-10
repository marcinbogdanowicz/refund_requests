from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.mixins import FlushRedisDBTestMixin
from apps.core.models import UserProfile
from apps.refunds.enums import RefundReason, RefundStatus
from apps.refunds.forms import RefundRequestForm
from apps.refunds.models import RefundRequest


class CreateRefundRequestViewTests(FlushRedisDBTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
        )
        cls.profile = UserProfile.objects.create(
            user=cls.user, phone_number='+48123456789'
        )
        cls.create_url = reverse('create_refund')
        cls.login_url = reverse('login')
        cls.valid_data = {
            'order_number': 'ORD123',
            'order_date': '2024-03-10',
            'products': 'Test Product',
            'reason_choice': RefundReason.WRONG_PRODUCT,
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+48123456789',
            'email': 'john@example.com',
            'address': 'Test Street 123',
            'postal_code': '12345',
            'city': 'Test City',
            'country': 'DE',
            'iban': 'DE89370400440532013000',
            'bank_name': 'Test Bank',
            'account_type': 'private',
        }

    def test_login_required(self):
        response = self.client.get(self.create_url)
        expected_url = f'{self.login_url}?next={self.create_url}'
        self.assertRedirects(response, expected_url)

    def test_get_shows_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refunds/create.html')
        self.assertIsInstance(response.context['form'], RefundRequestForm)

    @patch('apps.refunds.forms.RefundRequestForm.initial_for_user')
    def test_form_initialized_with_user_data(self, mock_initial):
        mock_initial.return_value = {}
        self.client.force_login(self.user)

        self.client.get(self.create_url)

        mock_initial.assert_called_once_with(self.user)

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_valid_post_creates_refund(self, mock_validate):
        mock_validate.return_value = {'valid': True, 'country': 'DE'}
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self.valid_data)

        self.assertRedirects(response, reverse('refund_list'))
        self.assertEqual(RefundRequest.objects.count(), 1)
        refund = RefundRequest.objects.first()
        self.assertEqual(refund.user, self.user)
        self.assertEqual(refund.order_number, 'ORD123')
        self.assertEqual(refund.status, RefundStatus.PENDING)
        self.assertTrue(refund.iban_verified)

    def test_reason_other(self):
        self.client.force_login(self.user)
        data = self.valid_data.copy()
        data['reason_choice'] = RefundReason.OTHER
        data['other_reason'] = 'Custom reason text'

        response = self.client.post(self.create_url, data)

        self.assertEqual(response.status_code, 302)
        refund = RefundRequest.objects.first()
        self.assertEqual(refund.reason, 'Custom reason text')

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_invalid_iban_shows_error(self, mock_validate):
        mock_validate.return_value = {'valid': False}
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            'Provided number is not a valid IBAN.',
        )
        self.assertEqual(RefundRequest.objects.count(), 0)

    @patch('apps.refunds.utils.APINinjasClient.validate_iban')
    def test_service_unavailable_creates_unverified(self, mock_validate):
        mock_validate.return_value = None
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self.valid_data)

        self.assertRedirects(response, reverse('refund_list'))
        refund = RefundRequest.objects.first()
        self.assertFalse(refund.iban_verified)

    def test_form_validation_required_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(self.create_url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'], 'order_number', 'This field is required.'
        )
        self.assertFormError(
            response.context['form'], 'products', 'This field is required.'
        )
        self.assertEqual(RefundRequest.objects.count(), 0)
