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
def authenticated_client():
    user = User.objects.get_or_create(username="testuser", password="testpass123456")
    client = APIClient()
    client.force_authenticate(user=user)
    return client
