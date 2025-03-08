from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from apps.core.forms import (
    BootstrapAuthenticationForm,
    BootstrapPasswordResetForm,
    BootstrapSetPasswordForm,
)
from apps.core.views import SignUpView
from apps.refunds.views import (
    CreateRefundRequestView,
    RefundRequestDetailView,
    RefundRequestListView,
)

urlpatterns = [
    path(
        '', RedirectView.as_view(url=reverse_lazy('refund_list')), name='home'
    ),
    path('admin/', admin.site.urls),
    path(
        'accounts/login/',
        LoginView.as_view(form_class=BootstrapAuthenticationForm),
        name='login',
    ),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path(
        'accounts/logout/',
        LogoutView.as_view(next_page=reverse_lazy('login')),
        name='logout',
    ),
    path(
        'accounts/password_reset/',
        PasswordResetView.as_view(
            template_name="registration/password_reset_generic.html",
            form_class=BootstrapPasswordResetForm,
            extra_context={
                "title": "Reset password",
                "message": "Reset link will be sent to your email.",
            },
        ),
        name='password_reset',
    ),
    path(
        'accounts/password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_generic.html",
            extra_context={
                "title": "Done",
                "message": "Check your email for reset link.",
            },
        ),
        name='password_reset_done',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_generic.html",
            form_class=BootstrapSetPasswordForm,
        ),
        name='password_reset_confirm',
    ),
    path(
        'accounts/reset/done/',
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_generic.html",
            extra_context={
                "title": "Done",
                "message": "Password reset successful.",
            },
        ),
        name='password_reset_complete',
    ),
    path(
        'refunds/',
        RefundRequestListView.as_view(),
        name='refund_list',
    ),
    path(
        'refunds/create/',
        CreateRefundRequestView.as_view(),
        name='create_refund',
    ),
    path(
        'refunds/<int:pk>/',
        RefundRequestDetailView.as_view(),
        name='refund_detail',
    ),
    # path('api/validate-iban/', ValidateIBANView.as_view(), name='validate_iban'),
]
