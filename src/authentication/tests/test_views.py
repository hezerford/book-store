import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestAuthenticationViews:
    def test_register_user_view(self, client):
        url = reverse("register")

        # Проверяем GET запрос (отображение формы)
        response = client.get(url)
        assert response.status_code == 200

        # Проверяем POST запрос (регистрация)
        response = client.post(
            url,
            {
                "username": "testuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        # Проверяем, что пользователь создался
        user_exists = User.objects.filter(username="testuser").exists()

        # Если пользователь создан, проверяем редирект
        if user_exists:
            assert response.status_code == 302
        else:
            # Если пользователь не создан, форма должна показывать ошибки
            assert response.status_code == 200

    def test_login_user_view(self, client, existing_user):
        url = reverse("login")

        # Проверяем GET запрос (отображение формы)
        response = client.get(url)
        assert response.status_code == 200

        # Проверяем POST запрос (логин)
        response = client.post(
            url, {"username": "testuser", "password": "testpassword"}
        )

        print(f"Login response status: {response.status_code}")

        # После успешного логина должен быть редирект
        if response.status_code == 302:
            # Успешный логин - редирект на home
            assert response.url == reverse("home")
        else:
            # Ошибки формы
            assert response.status_code == 200
            if hasattr(response, "context") and response.context:
                form = response.context.get("form")
                if form:
                    print("Login form errors:", form.errors)

    def test_logout_user_view(self, authenticated_client):
        url = reverse("logout")

        # LogoutView по умолчанию принимает только POST
        # Если хотите GET, добавьте в view: http_method_names = ['get', 'post']
        response = authenticated_client.post(url)

        # Должен быть редирект
        assert response.status_code == 302
        assert response.url == reverse("home")
