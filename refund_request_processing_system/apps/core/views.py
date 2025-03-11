from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from apps.core.forms import CustomUserCreationForm, UserProfileCreationForm


class SignUpView(TemplateView):
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = kwargs.get("user_form") or CustomUserCreationForm()
        context["profile_form"] = (
            kwargs.get("profile_form") or UserProfileCreationForm()
        )
        return context

    def post(self, request, *args, **kwargs):
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileCreationForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            self.create_user(user_form, profile_form)
            return redirect(self.success_url)

        return self.render_to_response(
            self.get_context_data(user_form=user_form, profile_form=profile_form)
        )

    @transaction.atomic()
    def create_user(self, user_form, profile_form):
        user = user_form.save()
        user_profile = profile_form.save(commit=False)
        user_profile.user = user
        user_profile.save()


def handler_404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler_500(request):
    return render(request, "errors/500.html", status=400)
