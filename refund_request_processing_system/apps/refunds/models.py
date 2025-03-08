from django.contrib.auth.models import User
from django.db import models


class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
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

    def __str__(self):
        return f"Refund #{self.id} - {self.order_number} - {self.status}"
