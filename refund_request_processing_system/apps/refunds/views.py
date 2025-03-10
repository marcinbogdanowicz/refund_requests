from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.refunds.forms import RefundRequestForm
from apps.refunds.models import RefundRequest
from apps.refunds.serializers import IBANSerializer
from apps.refunds.utils import IBANValidator


class CreateRefundRequestView(LoginRequiredMixin, CreateView):
    model = RefundRequest
    form_class = RefundRequestForm
    template_name = 'refunds/create.html'
    success_url = reverse_lazy('create_refund')

    def get_initial(self):
        return self.form_class.initial_for_user(self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RefundRequestListView(LoginRequiredMixin, ListView):
    model = RefundRequest
    template_name = 'refunds/list.html'
    context_object_name = 'refund_requests'
    paginate_by = 10

    def get_queryset(self):
        return RefundRequest.objects.filter(user=self.request.user)


class RefundRequestDetailView(DetailView):
    model = RefundRequest
    template_name = 'refunds/detail.html'
    context_object_name = 'refund_request'


class ValidateIBANView(APIView):
    def post(self, request):
        serializer = IBANSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            validator = IBANValidator(**data)
            return Response({'error': validator.get_error()})
        except RuntimeError as e:
            return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)
