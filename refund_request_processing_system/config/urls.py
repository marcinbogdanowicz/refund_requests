from apps.core.views import SignUpView
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    # path('accounts/logout/', LogoutView.as_view(), name='logout'),
    # path('refunds/', RefundRequestListView.as_view(), name='refund_list'),
    # path('refunds/create/', CreateRefundRequestView.as_view(), name='create_refund'),
    # path('refunds/<int:pk>/', RefundRequestDetailView.as_view(), name='refund_detail'),
    # path('api/validate-iban/', ValidateIBANView.as_view(), name='validate_iban'),
]
