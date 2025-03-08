from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from apps.refunds.forms import RefundRequestForm
from apps.refunds.models import RefundRequest


class CreateRefundRequestView(LoginRequiredMixin, CreateView):
    model = RefundRequest
    form_class = RefundRequestForm
    template_name = 'refunds/refund_request_form.html'
    success_url = reverse_lazy('create_refund')

    def get_initial(self):
        return self.form_class.initial_for_user(self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RefundRequestListView(LoginRequiredMixin, ListView):
    model = RefundRequest
    template_name = 'refunds/refund_request_list.html'
    context_object_name = 'refund_requests'

    def get_queryset(self):
        return RefundRequest.objects.filter(user=self.request.user)
