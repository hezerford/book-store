from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from .models import Cart, CartItem

from store.models import Book


# Получить существующую корзину или создать новую
def get_or_create_cart(request):
    if request.user.is_authenticated:
        # Пользователь авторизован, ищем или создаем корзину
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    else:
        # Если пользователь не авторизован, создаем сессию
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_key=session_key, is_active=True
        )

    return cart


def add_to_cart(request, book_slug):
    cart = get_or_create_cart(request)
    book = get_object_or_404(Book, slug=book_slug)

    # Устанавливаем цену с учетом скидки
    price = (
        book.discounted_price or book.price
    )  # Если указана цена со скидкой, используем её

    # Ищем существующую запись для этой книги
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, book=book, defaults={"price": price}
    )

    if not created:
        cart_item.quantity += 1  # Если запись уже есть, увеличиваем количество
    cart_item.save()

    return redirect("cart")
