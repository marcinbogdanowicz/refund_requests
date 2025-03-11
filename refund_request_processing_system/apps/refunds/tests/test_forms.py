from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.core.mixins import ClearCacheTestMixin
from apps.core.models import UserProfile
from apps.refunds.enums import RefundReason, RefundStatus
from apps.refunds.forms import RefundRequestForm
from apps.refunds.models import RefundRequest


class RefundRequestFormTests(ClearCacheTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        cls.profile = UserProfile.objects.create(
            user=cls.user, phone_number="+48123456789"
        )
        base_data = {
            "order_number": "ORD123",
            "order_date": "2024-03-10",
            "products": "Test Product",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+48123456789",
            "email": "john@example.com",
            "address": "Test Street 123",
            "postal_code": "12345",
            "city": "Test City",
            "country": "DE",
            "iban": "DE89370400440532013000",
            "bank_name": "Test Bank",
            "account_type": "private",
        }
        cls.base_data_model = base_data | {"reason": RefundReason.WRONG_PRODUCT}
        cls.base_data_form = base_data | {"reason_choice": RefundReason.WRONG_PRODUCT}

    def test_initial_data_new_user(self):
        form = RefundRequestForm(initial=RefundRequestForm.initial_for_user(self.user))

        self.assertEqual(form["first_name"].initial, "John")
        self.assertEqual(form["last_name"].initial, "Doe")
        self.assertEqual(form["email"].initial, "john@example.com")
        self.assertEqual(form["phone_number"].initial, "+48123456789")

        self.assertIsNone(form["iban"].initial)
        self.assertIsNone(form["bank_name"].initial)
        self.assertIsNone(form["account_type"].initial)
        self.assertIsNone(form["address"].initial)
        self.assertIsNone(form["postal_code"].initial)
        self.assertIsNone(form["city"].initial)
        self.assertIsNone(form["country"].initial)

    def test_initial_data_with_previous_request(self):
        RefundRequest.objects.create(
            user=self.user,
            order_number="OLD123",
            order_date=timezone.now().date(),
            products="Old Product",
            reason=RefundReason.WRONG_PRODUCT,
            status=RefundStatus.APPROVED,
            iban="DE89370400440532013000",
            iban_verified=True,
            bank_name="Old Bank",
            account_type="business",
            address="Old Address",
            postal_code="98765",
            city="Old City",
            country="DE",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+48123456789",
        )

        form = RefundRequestForm(initial=RefundRequestForm.initial_for_user(self.user))

        self.assertEqual(form["first_name"].initial, "John")
        self.assertEqual(form["last_name"].initial, "Doe")
        self.assertEqual(form["email"].initial, "john@example.com")
        self.assertEqual(form["phone_number"].initial, "+48123456789")

        self.assertEqual(form["address"].initial, "Old Address")
        self.assertEqual(form["postal_code"].initial, "98765")
        self.assertEqual(form["city"].initial, "Old City")
        self.assertEqual(form["iban"].initial, "DE89370400440532013000")
        self.assertEqual(form["bank_name"].initial, "Old Bank")
        self.assertEqual(form["account_type"].initial, "business")

    @patch("apps.refunds.utils.APINinjasClient.validate_iban")
    def test_previously_validated_iban_is_cached(self, mock_validate):
        RefundRequest.objects.create(
            **self.base_data_model, user=self.user, iban_verified=True
        )

        form = RefundRequestForm(initial=RefundRequestForm.initial_for_user(self.user))
        mock_validate.assert_not_called()

        form = RefundRequestForm(self.base_data_form)
        self.assertTrue(form.is_valid())
        mock_validate.assert_not_called()

    def test_reason_choice_from_standard_reason(self):
        refund_request = RefundRequest.objects.create(
            **self.base_data_model
            | {"user": self.user, "reason": RefundReason.WRONG_PRODUCT}
        )

        form = RefundRequestForm(instance=refund_request)
        self.assertEqual(form["reason_choice"].initial, RefundReason.WRONG_PRODUCT)
        self.assertEqual(form["other_reason"].initial, None)

    def test_reason_choice_from_custom_reason(self):
        refund_request = RefundRequest.objects.create(
            **self.base_data_model | {"user": self.user, "reason": "Custom reason text"}
        )

        form = RefundRequestForm(instance=refund_request)
        self.assertEqual(form["reason_choice"].initial, RefundReason.OTHER)
        self.assertEqual(form["other_reason"].initial, "Custom reason text")

    def test_save_standard_reason(self):
        data = self.base_data_form.copy()
        data["reason_choice"] = RefundReason.PRODUCT_DAMAGED
        form = RefundRequestForm(data)

        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.reason, RefundReason.PRODUCT_DAMAGED)

    def test_save_other_reason(self):
        data = self.base_data_form.copy()
        data["reason_choice"] = RefundReason.OTHER
        data["other_reason"] = "Custom reason text"
        form = RefundRequestForm(data)

        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.reason, "Custom reason text")

    def test_other_reason_required_when_other_selected(self):
        data = self.base_data_form.copy()
        data["reason_choice"] = RefundReason.OTHER
        data["other_reason"] = ""
        form = RefundRequestForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn("other_reason", form.errors)

    @patch("apps.refunds.utils.APINinjasClient.validate_iban")
    def test_iban_validation_success(self, mock_validate):
        mock_validate.return_value = {"valid": True, "country": "DE"}
        form = RefundRequestForm(self.base_data_form)

        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertTrue(instance.iban_verified)

    @patch("apps.refunds.utils.APINinjasClient.validate_iban")
    def test_iban_validation_failure(self, mock_validate):
        mock_validate.return_value = {"valid": False}
        form = RefundRequestForm(self.base_data_form)

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn("valid IBAN", form.errors["__all__"][0])

    @patch("apps.refunds.utils.APINinjasClient.validate_iban")
    def test_iban_validation_service_unavailable(self, mock_validate):
        mock_validate.return_value = None
        form = RefundRequestForm(self.base_data_form)
        form.instance.user = self.user

        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertFalse(instance.iban_verified)
