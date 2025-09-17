import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.test import APIClient
from mixer.backend.django import mixer

from store.models import Book, Subscription
from cart.models import Cart, CartItem
from user_profile.models import UserProfile


@pytest.fixture(autouse=True)
def clear_cache():
    """Удаляем кэш перед тестами"""
    cache.clear()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    """Создаем временно хранилище в памяти для теста медия файлов"""
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def force_test_email_backend(settings):
    """Используем локальную память для эмитации отправки писем"""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture(autouse=True)
def celery_run_eager(settings):
    """Делает задачи синхронными для лучшего захвата ошибок."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture(autouse=True)
def disable_axes_for_tests(settings):
    """Используется только ModelBackend для тестов, чтобы исключить влияние каптчи"""
    settings.AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
    ]


@pytest.fixture
def create_book():
    def _create_book(**kwargs):
        # Безопасные значения по умолчанию и корректировка скидки под CheckConstraint
        price = kwargs.get("price", 20.00)
        kwargs["price"] = price

        if "discounted_price" not in kwargs:
            # По умолчанию без скидки
            kwargs["discounted_price"] = None
        else:
            dp = kwargs.get("discounted_price")
            if dp is not None and dp >= price:
                # Корректируем скидку, чтобы соблюсти ограничение БД
                kwargs["discounted_price"] = round(float(price) - 0.01, 2)

        return mixer.blend(Book, **kwargs)

    return _create_book


@pytest.fixture
def create_three_books():
    def _create_books():
        # Явно задаём валидные значения, чтобы не нарушать констрейнт
        return mixer.cycle(3).blend(
            Book,
            price=20.00,
            discounted_price=None,
            photo="/static/img/default-book.png",
        )

    return _create_books


@pytest.fixture
def existing_user():
    # Создаем пользователя для тестов
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def authenticated_API_client(existing_user):
    client = APIClient()
    client.force_authenticate(user=existing_user)
    client.user = existing_user
    return client


@pytest.fixture
def authenticated_client(existing_user):
    client = Client()
    client.force_login(existing_user)
    return client


@pytest.fixture
def create_cart_with_items(existing_user, create_book):
    cart = Cart.objects.create(user=existing_user, is_active=True)

    for i in range(3):
        book = create_book()
        CartItem.objects.create(cart=cart, book=book, quantity=i + 1, price=book.price)

    return cart


@pytest.fixture
def create_cart():
    """Создаёт корзину для тестов."""

    def _create_cart(user=None, session_key=None, created_at=None, is_active=True):
        cart = Cart.objects.create(
            user=user,
            session_key=session_key or "test_session",
            is_active=is_active,
        )
        if created_at:
            cart.created_at = created_at
            cart.save()
        return cart

    return _create_cart


@pytest.fixture
def create_user_profile(existing_user):
    def _create_user_profile(**kwargs):
        return UserProfile.objects.create(user=existing_user, **kwargs)

    return _create_user_profile


@pytest.fixture
def create_subscription():
    def _create_subscription(**kwargs):
        return mixer.blend(Subscription, **kwargs)

    return _create_subscription
