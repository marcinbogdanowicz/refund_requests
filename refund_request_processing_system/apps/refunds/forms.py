from django import forms

from apps.refunds.models import RefundRequest


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = [
            'order_number',
            'order_date',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'country',
            'address',
            'postal_code',
            'city',
            'products',
            'reason',
            'bank_name',
            'account_type',
            'iban',
        ]

    @classmethod
    def initial_for_user(cls, user):
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.userprofile.phone_number,
        }
