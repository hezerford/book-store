import pytest

from django.test import Client
from django.urls import reverse

from authentication.forms import LoginUserForm, RegisterUserForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    "form_data, is_valid, error_fields",
    [
        (
            {
                "username": "validuser",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
            True,
            [],
        ),
        (
            {
                "username": "testuser",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
            False,
            ["username"],
        ),
        (
            {
                "username": "validuser",
                "password1": "WeakPas",
                "password2": "WeakPas",
            },
            False,
            ["password2"],
        ),
        (
            {
                "username": "validuser",
                "password1": "StrongPass123",
                "password2": "WrongPass123",
            },
            False,
            ["password2"],
        ),
    ],
)
def test_register_user_form(form_data, is_valid, error_fields, existing_user):
    form = RegisterUserForm(data=form_data)
    assert form.is_valid() == is_valid

    for field in error_fields:
        assert field in form.errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "form_data, is_valid, error_fields",
    [
        ({"username": "testuser", "password": "testpassword"}, True, []),
        (
            {"username": "nonexistentuser", "password": "testpassword"},
            False,
            ["__all__"],
        ),
        (
            {"username": "testuser", "password": "wrongpassword"},
            False,
            ["__all__"],
        ),
    ],
)
def test_login_user_form(form_data, is_valid, error_fields, existing_user):
    form = LoginUserForm(data=form_data)
    assert form.is_valid() == is_valid

    for field in error_fields:
        assert field in form.errors


@pytest.mark.django_db
def test_successful_login(existing_user):
    client = Client()

    logged_in = client.login(username="testuser", password="testpassword")
    assert logged_in is True

    url = reverse("cart")
    response = client.get(url)

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == "testuser"
