from django.urls import reverse
import pytest
from cart.models import Cart, CartItem
from store.models import Book
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_cart_clear(create_cart_with_items):
    # Тест, что корзина очищается
    cart = create_cart_with_items
    cart.clear()

    assert cart.items.count() == 0
    assert not cart.is_active


@pytest.mark.django_db
def test_cart_assign_to_user(existing_user):
    # Создаем корзину без привязки к пользователю (например, для анонимного)
    cart = Cart.objects.create(session_key="test_session_key", is_active=True)

    # Проверяем начальное состояние корзины
    assert cart.user is None
    assert cart.session_key == "test_session_key"

    # Привязываем корзину к существующему пользователю
    cart.assign_to_user(existing_user)

    # Проверяем, что корзина теперь привязана к пользователю
    assert cart.user == existing_user
    assert cart.session_key is None  # session_key должен быть очищен


@pytest.mark.django_db
def test_cart_total_price(create_cart_with_items):
    # Тест, что цена считается правильно
    cart = create_cart_with_items
    total_price = cart.get_total_price()

    expected_price = sum(item.price * item.quantity for item in cart.cartitem_set.all())
    assert total_price == expected_price


@pytest.mark.django_db
def test_cart_total_items(create_cart_with_items):
    # Тест, что количество объектов соотвествует в корзине
    cart = create_cart_with_items
    total_items = cart.get_total_items()

    expected_items = sum(item.quantity for item in cart.cartitem_set.all())
    assert total_items == expected_items
