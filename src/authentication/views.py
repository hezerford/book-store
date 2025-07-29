from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin

from django.db import transaction

from user_profile.models import UserProfile

from .forms import RegisterUserForm, LoginUserForm


class RegisterUserView(UserPassesTestMixin, CreateView):
    form_class = RegisterUserForm
    template_name = "authentication/register.html"

    def test_func(self):
        return not self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register"
        return context

    @transaction.atomic
    def form_valid(self, form):  # Убран лишний параметр request
        try:
            # Передаем request через self.request
            user = form.save(request=self.request)
            UserProfile.objects.create(user=user)
            login(
                self.request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect("home")
        except Exception as e:
            form.add_error(None, f"Error creating user: {str(e)}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("home")


class LoginUserView(UserPassesTestMixin, LoginView):
    form_class = LoginUserForm
    template_name = "authentication/login.html"

    def test_func(self):
        return not self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Authorization"
        context["username"] = (
            self.request.user.username if self.request.user.is_authenticated else None
        )
        return context

    def get_success_url(self):
        return reverse_lazy("home")


class LogoutUserView(LogoutView):
    next_page = reverse_lazy("home")

    # Если хотите, чтобы logout работал по GET запросу:
    http_method_names = ["get", "post", "options"]  # Разрешаем GET
