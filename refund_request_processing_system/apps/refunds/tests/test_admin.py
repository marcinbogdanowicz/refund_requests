from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils.safestring import SafeString

from apps.refunds.admin import RefundRequestAdmin
from apps.refunds.enums import RefundStatus
from apps.refunds.models import RefundRequest


class RefundRequestAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        cls.site = AdminSite()
        cls.request_factory = RequestFactory()
        cls.request = cls.request_factory.get("/admin")
        cls.request.user = cls.admin_user

        cls.refund = RefundRequest.objects.create(
            user=cls.admin_user,
            order_number="ORD123",
            order_date="2024-03-10",
            products="Test Product",
            reason="Test Reason",
            status=RefundStatus.PENDING,
            first_name="John",
            last_name="Doe",
            phone_number="+48123456789",
            email="john@example.com",
            address="Test Street 123",
            postal_code="12345",
            city="Test City",
            country="DE",
            iban="DE89370400440532013000",
            bank_name="Test Bank",
            account_type="personal",
            notes="Test notes\nSecond line\nThird line\nFourth line\nFifth line\nSixth line\nSeventh line",
        )

    @property
    def admin(self):
        return RefundRequestAdmin(RefundRequest, self.site)

    def test_full_name_display(self):
        self.assertEqual(self.admin.full_name(self.refund), "John Doe")

    def test_notes_preview_shortens_text(self):
        preview = self.admin.notes_preview(self.refund)
        self.assertLess(len(preview), len(self.refund.notes))
        self.assertTrue(preview.endswith("[...]"))

    @patch("apps.refunds.models.RefundRequest.emit_status_change_email")
    def test_approve_refund_requests(self, mock_emit):
        queryset = RefundRequest.objects.filter(id=self.refund.id)
        self.admin.approve_refund_requests(self.request, queryset)

        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, RefundStatus.APPROVED)
        mock_emit.assert_called_once()

    @patch("apps.refunds.models.RefundRequest.emit_status_change_email")
    @patch("apps.refunds.admin.RefundRequestAdmin.message_user")
    def test_cannot_approve_rejected_refunds(self, mock_message_user, mock_emit):
        self.refund.status = RefundStatus.REJECTED
        self.refund.save()

        queryset = RefundRequest.objects.filter(id=self.refund.id)
        self.admin.approve_refund_requests(self.request, queryset)

        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, RefundStatus.REJECTED)
        mock_emit.assert_not_called()

        mock_message_user.assert_called_once()
        self.assertIn(
            "Can't approve the following refund requests with status 'Rejected'",
            mock_message_user.call_args[0][1],
        )

    @patch("apps.refunds.models.RefundRequest.emit_status_change_email")
    def test_reject_refund_requests(self, mock_emit):
        queryset = RefundRequest.objects.filter(id=self.refund.id)
        self.admin.reject_refund_requests(self.request, queryset)

        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, RefundStatus.REJECTED)
        mock_emit.assert_called_once()

    @patch("apps.refunds.models.RefundRequest.emit_status_change_email")
    @patch("apps.refunds.admin.RefundRequestAdmin.message_user")
    def test_cannot_reject_approved_refunds(self, mock_message_user, mock_emit):
        self.refund.status = RefundStatus.APPROVED
        self.refund.save()

        queryset = RefundRequest.objects.filter(id=self.refund.id)
        self.admin.reject_refund_requests(self.request, queryset)

        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, RefundStatus.APPROVED)
        mock_emit.assert_not_called()

        mock_message_user.assert_called_once()
        self.assertIn(
            "Can't reject the following refund requests with status 'Approved'",
            mock_message_user.call_args[0][1],
        )

    @patch("apps.refunds.utils.IBANValidator.get_error")
    @patch("apps.refunds.admin.RefundRequestAdmin.message_user")
    def test_validate_iban_success(self, mock_message_user, mock_get_error):
        mock_get_error.return_value = None
        queryset = RefundRequest.objects.filter(id=self.refund.id)

        self.admin.validate_iban(self.request, queryset)
        message = mock_message_user.call_args[0][1]

        self.assertIsInstance(message, SafeString)
        self.assertIn(str(self.refund.id), str(message))
        self.assertIn("successfully validated", str(message))

    @patch("apps.refunds.utils.IBANValidator.get_error")
    @patch("apps.refunds.admin.RefundRequestAdmin.message_user")
    def test_validate_iban_failure(self, mock_message_user, mock_get_error):
        mock_get_error.return_value = "Invalid IBAN"
        queryset = RefundRequest.objects.filter(id=self.refund.id)

        self.admin.validate_iban(self.request, queryset)
        message = mock_message_user.call_args[0][1]

        self.assertIsInstance(message, SafeString)
        self.assertIn(str(self.refund.id), str(message))
        self.assertIn("Invalid IBAN", str(message))

    def test_import_permission_denied(self):
        self.assertFalse(self.admin.has_import_permission(self.request))
