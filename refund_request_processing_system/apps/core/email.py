from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone


class BaseEmailMessage(models.Model):
    recipients = models.ManyToManyField(User)
    sent_at = models.DateTimeField(null=True, blank=True)

    from_email = settings.DEFAULT_FROM_EMAIL
    cc = None
    bcc = None

    @property
    def template_name(self):
        raise NotImplementedError

    @property
    def subject(self):
        raise NotImplementedError

    def get_email_context(self, user):
        raise NotImplementedError

    def send(self):
        for user in self.recipients.all():
            email_context = self.get_email_context(user)

            txt_content = self.get_txt_content(email_context)
            html_content = self.get_html_content(email_context)

            email = EmailMultiAlternatives(
                subject=self.subject,
                body=txt_content,
                from_email=self.from_email,
                to=[user.email],
                cc=self.cc,
                bcc=self.bcc,
            )
            email.attach_alternative(html_content, "text/html")

            email.send()

        self.sent_at = timezone.now()
        self.save(update_fields=["sent_at"])

    def get_txt_content(self, context):
        return render_to_string(f"{self.template_name}.txt", context)

    def get_html_content(self, context):
        return render_to_string(f"{self.template_name}.html", context)

    class Meta:
        abstract = True
