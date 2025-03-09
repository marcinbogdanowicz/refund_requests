from django.contrib import admin
from django.db.models import Case, IntegerField, Value, When
from django.utils.safestring import mark_safe

from apps.core.utils import comma_join_str
from apps.refunds.enums import RefundStatus
from apps.refunds.models import RefundRequest


class RefundRequestAdmin(admin.ModelAdmin):
    model = RefundRequest
    list_display = [
        'id',
        'status',
        'iban_verified',
        'created_at',
        'updated_at',
        'order_number',
        'full_name',
        'email',
        'phone_number',
        'country',
    ]

    readonly_fields = [
        'user',
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
        'iban_verified',
        'created_at',
        'updated_at',
        'status',
    ]

    list_filter = ['status', 'created_at', 'country']

    actions = [
        'approve_refund_requests',
        'reject_refund_requests',
        'mark_refund_requests_as_pending',
    ]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.action(description='Approve')
    def approve_refund_requests(self, request, queryset):
        rejected_refund_requests_ids = list(
            queryset.filter(status=RefundStatus.REJECTED).values_list(
                'id', flat=True
            )
        )
        if rejected_refund_requests_ids:
            self.message_user(
                request,
                mark_safe(
                    "<p>Can't approve the following refund requests with status "
                    f"'Rejected': {comma_join_str(rejected_refund_requests_ids)}</p>"
                    "<p>If you are sure these should be approved, assign them "
                    "'Pending' status first"
                ),
                level='ERROR',
            )
            return
        self._change_refund_requests_status(queryset, RefundStatus.APPROVED)

    @admin.action(description='Reject')
    def reject_refund_requests(self, request, queryset):
        approved_refund_requests_ids = list(
            queryset.filter(status=RefundStatus.APPROVED).values_list(
                'id', flat=True
            )
        )
        if approved_refund_requests_ids:
            self.message_user(
                request,
                mark_safe(
                    "<p>Can't reject the following refund requests with status "
                    f"'Approved': {comma_join_str(approved_refund_requests_ids)}</p>"
                    "<p>If you are sure these should be rejected, assign them "
                    "'Pending' status first"
                ),
                level='ERROR',
            )
            return
        self._change_refund_requests_status(queryset, RefundStatus.REJECTED)

    @admin.action(description='Mark as pending')
    def mark_refund_requests_as_pending(self, request, queryset):
        self._change_refund_requests_status(queryset, RefundStatus.PENDING)

    def _change_refund_requests_status(self, queryset, status):
        queryset.update(status=status)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _status_order=Case(
                When(status=RefundStatus.PENDING, then=Value(1)),
                When(status=RefundStatus.APPROVED, then=Value(2)),
                When(status=RefundStatus.REJECTED, then=Value(3)),
                output_field=IntegerField(),
            )
        ).order_by('_status_order', '-created_at')


admin.site.register(RefundRequest, RefundRequestAdmin)
