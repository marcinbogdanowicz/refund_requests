from django import forms

from apps.core.mixins import BootstrapFormMixin
from apps.refunds.models import RefundRequest


class RefundRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = [
            'order_number',
            'order_date',
            'products',
            'reason',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'bank_name',
            'account_type',
            'iban',
            'country',
            'address',
            'postal_code',
            'city',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'products': forms.Textarea(attrs={'rows': 3}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    @classmethod
    def initial_for_user(cls, user):
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.userprofile.phone_number,
        }
