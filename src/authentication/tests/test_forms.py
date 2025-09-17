import pytest
from django.test import Client, RequestFactory
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

    # Удаляем капчу из формы в тестах
    if "captcha" in form.fields:
        del form.fields["captcha"]

    assert form.is_valid() == is_valid

    for field in error_fields:
        assert field in form.errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "form_data, is_valid, error_fields",
    [
        ({"username": "testuser", "password": "testpassword"}, True, []),
    ],
)
def test_login_user_form(form_data, is_valid, error_fields, existing_user):
    factory = RequestFactory()
    request = factory.post("/login/")
    request.session = {}
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    form = LoginUserForm(data=form_data, request=request)

    # Удаляем капчу из формы в тестах
    if "captcha" in form.fields:
        del form.fields["captcha"]

    form_is_valid = form.is_valid()

    if form_is_valid != is_valid:
        print(f"Expected is_valid={is_valid}, got {form_is_valid}")
        print(f"Form errors: {form.errors}")

    assert form_is_valid == is_valid

    for field in error_fields:
        assert field in form.errors


@pytest.mark.django_db
def test_successful_login(existing_user):
    from django.contrib.auth import authenticate

    # Создаем request для аутентификации через axes
    factory = RequestFactory()
    request = factory.post("/login/")
    request.session = {}
    request.META["REMOTE_ADDR"] = "127.0.0.1"  # IP адрес для axes

    # Аутентифицируемся через authenticate с правильными данными
    user = authenticate(request, username="testuser", password="testpassword")

    assert user is not None
    assert user.is_active
