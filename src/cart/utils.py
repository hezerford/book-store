from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from .models import Cart, CartItem

from store.models import Book
from django.contrib.auth.models import AnonymousUser


def get_or_create_cart(request):
    """
    Получает или создает корзину для пользователя или сессии.
    """
    if request.user.is_authenticated:
        # Для авторизованного пользователя
        cart, created = Cart.objects.get_or_create(
            user=request.user, is_active=True, defaults={"user": request.user}
        )
    else:
        # Для гостя - используем session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            is_active=True,
            defaults={"session_key": session_key},
        )

    return cart


def merge_guest_cart_with_user_cart(request, user):
    """
    Сливает гостевую корзину с корзиной пользователя при логине.
    """
    if not request.session.session_key:
        return  # Нет гостевой корзины

    # Получаем гостевую корзину
    guest_cart = Cart.objects.filter(
        session_key=request.session.session_key, is_active=True
    ).first()

    if not guest_cart:
        return  # Гостевая корзина пуста

    # Получаем или создаем корзину пользователя
    user_cart, created = Cart.objects.get_or_create(
        user=user, is_active=True, defaults={"user": user}
    )

    # Сливаем корзины
    user_cart.merge_with(guest_cart)

    # Деактивируем гостевую корзину
    guest_cart.is_active = False
    guest_cart.save()

    return user_cart


def get_cart_items_count(request):
    """
    Возвращает количество товаров в корзине для отображения в шапке.
    """
    try:
        cart = get_or_create_cart(request)
        return cart.get_total_items()
    except:
        return 0


def add_to_cart(request, book_slug):
    """Добавляет книгу в корзину."""

    cart = get_or_create_cart(request)
    book = get_object_or_404(Book, slug=book_slug)

    # Устанавливаем цену с учетом скидки
    price = (
        book.discounted_price or book.price
    )  # Если указана цена со скидкой, используем её

    # Ищем существующую запись для этой книги
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, book=book, defaults={"price": price, "quantity": 0}
    )

    # Обновляем цену (на случай, если она изменилась)
    cart_item.price = price
    # Увеличиваем количество только если элемент уже существовал
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1  # или 0, если по умолчанию 0
    cart_item.save()

    return redirect("cart")
