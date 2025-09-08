from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User

from captcha.fields import CaptchaField


class RegisterUserForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "The two password field didn't match.",
    }

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-input"}),
        error_messages={"unique": "This username is already taken."},
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        help_text="Password must be at least 8 characters long and contain both letters and numbers.",
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r"^(?=.*[A-Za-z])(?=.*\d)",
                message="Password must contain both letters and numbers.",
            ),
        ],
    )
    password2 = forms.CharField(
        label="Repeat Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    captcha = CaptchaField(
        label="Enter Captcha", error_messages={"invalid": "Invalid captcha"}
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class LoginUserForm(AuthenticationForm):

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    captcha = CaptchaField(
        label="Enter Captcha", error_messages={"invalid": "Invalid captcha"}
    )
