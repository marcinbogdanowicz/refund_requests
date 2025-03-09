from django.db import models

from apps.core.email import BaseEmailMessage


class RefundRequestStatusChangeEmailMessage(BaseEmailMessage):
    refund_request = models.ForeignKey(
        'refunds.RefundRequest',
        on_delete=models.CASCADE,
        related_name="status_change_emails",
    )
    new_status = models.CharField(max_length=20)

    template_name = "refunds/emails/request_status_change"

    @property
    def subject(self):
        return f"Status update for refund request #{self.refund_request.id}"

    def get_email_context(self, user):
        return {
            "first_name": user.first_name,
            "new_status": self.new_status,
            "refund_request": self.refund_request,
        }
