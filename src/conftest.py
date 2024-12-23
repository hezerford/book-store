import pytest
from rest_framework.test import APIClient
from mixer.backend.django import mixer
from store.models import Book
from django.contrib.auth.models import User


@pytest.fixture
def create_book():
    def _create_book(**kwargs):
        return mixer.blend(Book, photo=None, **kwargs)

    return _create_book


@pytest.fixture
def create_three_books():
    def _create_books():
        return mixer.cycle(3).blend(Book, photo=None)

    return _create_books


@pytest.fixture
def existing_user():
    # Создаем пользователя для тестов
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def authenticated_client():
    client = APIClient()
    client.force_authenticate(existing_user)
    return client
