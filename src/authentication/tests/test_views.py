import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_register_user_view(client):
    url = reverse("register")
    response = client.post(
        url,
        {
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        },
    )

    assert response.status_code == 302
    # Проверяем что пользователь с указанным именем зарегестрировался
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_login_user_view(client, existing_user, create_book):
    url = reverse("login")
    response = client.post(url, {"username": "testuser", "password": "testpassword"})
    assert response.status_code == 302  # Проверяем что авторизация прошла успешно

    assert response.url == reverse("home")


@pytest.mark.django_db
def test_logout_user_view(authenticated_client):
    url = reverse("logout")
    response = authenticated_client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("home")  # Проверяем редирект на страницу входа
    # Проверяем, что пользователь разлогинился
    assert not response.wsgi_request.user.is_authenticated
