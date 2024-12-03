from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView

from .forms import RegisterUserForm, LoginUserForm


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "authentication/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register"
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("home")

    def get_success_url(self):
        return reverse_lazy("home")


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = "authentication/login.html"

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
