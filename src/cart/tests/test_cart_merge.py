import pytest
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from cart.utils import merge_guest_cart_with_user_cart
from store.models import Book


@pytest.mark.django_db
def test_merge_guest_cart_with_user_cart(create_book):
    """Тест слияния гостевой корзины с корзиной пользователя."""
    # Создаем пользователя
    user = User.objects.create_user(username="testuser", password="testpass")

    # Создаем книги
    book1 = create_book(title="Book 1", price=10.00)
    book2 = create_book(title="Book 2", price=20.00)
    book3 = create_book(title="Book 3", price=15.00)

    # Создаем гостевую корзину
    guest_cart = Cart.objects.create(session_key="test_session_key", is_active=True)
    CartItem.objects.create(cart=guest_cart, book=book1, quantity=2, price=10.00)
    CartItem.objects.create(cart=guest_cart, book=book2, quantity=1, price=20.00)

    # Создаем корзину пользователя с одним товаром
    user_cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(
        cart=user_cart, book=book1, quantity=1, price=10.00
    )  # Тот же товар
    CartItem.objects.create(
        cart=user_cart, book=book3, quantity=3, price=15.00
    )  # Другой товар

    # Создаем mock request
    class MockRequest:
        def __init__(self):
            self.session = type(
                "MockSession", (), {"session_key": "test_session_key"}
            )()

    request = MockRequest()

    # Выполняем слияние
    result_cart = merge_guest_cart_with_user_cart(request, user)

    # Проверяем результат
    assert result_cart == user_cart

    # Проверяем, что товары слились правильно
    cart_items = user_cart.cartitem_set.all()

    # Должно быть 3 товара: book1 (2+1=3), book2 (1), book3 (3)
    assert cart_items.count() == 3

    # Проверяем количество для book1 (должно быть 3)
    book1_item = cart_items.filter(book=book1).first()
    assert book1_item.quantity == 3

    # Проверяем количество для book2 (должно быть 1)
    book2_item = cart_items.filter(book=book2).first()
    assert book2_item.quantity == 1

    # Проверяем количество для book3 (должно быть 3)
    book3_item = cart_items.filter(book=book3).first()
    assert book3_item.quantity == 3

    # Проверяем общую сумму
    expected_total = (3 * 10.00) + (1 * 20.00) + (3 * 15.00)  # 30 + 20 + 45 = 95
    assert user_cart.get_total_price() == expected_total

    # Проверяем общее количество товаров
    assert user_cart.get_total_items() == 7  # 3 + 1 + 3

    # Проверяем, что гостевая корзина деактивирована
    guest_cart.refresh_from_db()
    assert not guest_cart.is_active


@pytest.mark.django_db
def test_merge_empty_guest_cart(create_book):
    """Тест слияния пустой гостевой корзины."""
    user = User.objects.create_user(username="testuser", password="testpass")
    book = create_book(title="Book 1", price=10.00)

    # Создаем корзину пользователя
    user_cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(cart=user_cart, book=book, quantity=1, price=10.00)

    # Создаем mock request без гостевой корзины
    class MockRequest:
        def __init__(self):
            self.session = type("MockSession", (), {"session_key": None})()

    request = MockRequest()

    # Выполняем слияние
    result_cart = merge_guest_cart_with_user_cart(request, user)

    # Проверяем, что корзина пользователя не изменилась
    assert result_cart is None
    assert user_cart.cartitem_set.count() == 1
    assert user_cart.get_total_price() == 10.00


@pytest.mark.django_db
def test_cart_merge_with_same_cart():
    """Тест слияния корзины с самой собой."""
    user = User.objects.create_user(username="testuser", password="testpass")
    cart = Cart.objects.create(user=user, is_active=True)

    # Попытка слияния с самой собой
    cart.merge_with(cart)

    # Корзина должна остаться без изменений
    assert cart.cartitem_set.count() == 0
    assert cart.get_total_price() == 0
