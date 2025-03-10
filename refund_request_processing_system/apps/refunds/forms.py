from contextlib import suppress

from django import forms
from django.core.exceptions import ValidationError

from apps.core.mixins import BootstrapFormMixin
from apps.refunds.enums import RefundReason
from apps.refunds.models import RefundRequest
from apps.refunds.utils import IBANValidator


class RefundRequestForm(BootstrapFormMixin, forms.ModelForm):
    reason_choice = forms.ChoiceField(
        choices=RefundReason.as_choices(), required=True, label='Reason'
    )
    other_reason = forms.CharField(required=False)

    class Meta:
        model = RefundRequest
        fields = [
            'order_number',
            'order_date',
            'products',
            'reason_choice',
            'other_reason',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address',
            'postal_code',
            'city',
            'country',
            'iban',
            'bank_name',
            'account_type',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'products': forms.Textarea(attrs={'rows': 3}),
            'other_reason': forms.Textarea(attrs={'rows': 3}),
            'iban': forms.TextInput(
                attrs={'pattern': '[A-Z]{2}[0-9]{2}[0-9A-Z]{1,30}'}
            ),
        }
        help_texts = {
            'iban': 'Only digits and upper case letters. E.g. \'PL10105000997603123456789123\'',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.reason not in RefundReason:
                self.fields['reason_choice'].initial = RefundReason.OTHER
                self.fields['other_reason'].initial = self.instance.reason
            else:
                self.fields['reason_choice'].initial = self.instance.reason

    @classmethod
    def initial_for_user(cls, user):
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.userprofile.phone_number,
        }

        if last_request := RefundRequest.objects.filter(user=user).last():
            initial.update(
                {
                    'address': last_request.address,
                    'postal_code': last_request.postal_code,
                    'city': last_request.city,
                    'country': last_request.country,
                    'iban': last_request.iban,
                    'bank_name': last_request.bank_name,
                    'account_type': last_request.account_type,
                }
            )

            if last_request.iban_verified:
                IBANValidator(
                    last_request.iban, last_request.country
                ).cache_valid_iban()

        return initial

    def clean(self):
        cleaned_data = super().clean()
        self._custom_clean_iban(cleaned_data)
        self._custom_clean_reason(cleaned_data)

        return cleaned_data

    def _custom_clean_iban(self, cleaned_data):
        iban = cleaned_data.get('iban')
        country = cleaned_data.get('country')

        iban_validator = IBANValidator(iban, country)
        with suppress(RuntimeError):
            if error := iban_validator.get_error():
                raise ValidationError(error, code='invalid')

            self.instance.iban_verified = True

    def _custom_clean_reason(self, cleaned_data):
        reason_choice = cleaned_data.get('reason_choice')
        other_reason = cleaned_data.get('other_reason')

        if reason_choice == RefundReason.OTHER:
            if not other_reason:
                self.add_error('other_reason', 'This field is required.')
            else:
                self.instance.reason = other_reason
        else:
            self.instance.reason = reason_choice
