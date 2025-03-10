from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from apps.refunds.email import RefundRequestStatusChangeEmailMessage
from apps.refunds.enums import RefundStatus


class RefundRequest(models.Model):
    STATUS_CHOICES = [
        (RefundStatus.PENDING, 'Pending'),
        (RefundStatus.APPROVED, 'Approved'),
        (RefundStatus.REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='refund_requests'
    )

    order_number = models.CharField(max_length=100)
    order_date = models.DateField()

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    country = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    products = models.TextField()
    reason = models.TextField()

    bank_name = models.CharField(max_length=200)
    account_type = models.CharField(
        max_length=20,
        choices=[('business', 'Business'), ('private', 'Private')],
    )
    iban = models.CharField(max_length=34)
    iban_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Refund #{self.id} - {self.order_number} - {self.status}"

    @property
    def full_link(self):
        return settings.BASE_URL + reverse('refund_detail', args=[self.id])

    def emit_status_change_email(self):
        email_message = RefundRequestStatusChangeEmailMessage.objects.create(
            refund_request=self,
            new_status=self.status,
        )
        email_message.recipients.add(self.user)
        email_message.send()

    class Meta:
        ordering = ('-created_at',)
