import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpass12345')

@pytest.mark.django_db(transaction=True)
def test_register_user_view(client):
    response = client.post(reverse('register'), {'username': 'testuser', 'password1': 'testpass12345', 'password2': 'testpass12345'})
    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists() # Проверяем что пользователь с указанным именем зарегестрировался

@pytest.mark.django_db(transaction=True)
def test_login_user_view(client, test_user):
    response = client.post(reverse('login'), {'username': b'testuser', 'password': b'testpass12345'})
    assert response.status_code == 200 # Проверяем что авторизация прошла успешно

@pytest.mark.django_db(transaction=True)
def test_logout_user_view(client, test_user):
    client.force_login(test_user)
    response = client.get(reverse('logout'))
    assert response.status_code == 302
    assert not client.session.get('_auth_user_id') # Проверяем, что пользователь вышел из системы