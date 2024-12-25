import pytest
from django.urls import reverse
from cart.models import Cart, CartItem
from store.models import Book
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_cart_view(authenticated_client, create_cart_with_items):
    url = reverse("cart")
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert "cart_items" in response.context
    assert "total_price" in response.context
    assert "total_items" in response.context


@pytest.mark.django_db
def test_add_to_cart_view(authenticated_client, create_book):
    book = create_book()
    url = reverse("add-to-cart", kwargs={"book_slug": book.slug})

    response = authenticated_client.post(url)

    assert response.status_code == 302
    assert CartItem.objects.filter(book=book).exists()


@pytest.mark.django_db
def test_remove_from_cart_view(authenticated_client, create_cart_with_items):
    # Получаем элемент корзины
    cart_item = CartItem.objects.first()
    url = reverse("remove-from-cart", kwargs={"book_slug": cart_item.book.slug})

    # Отправляем POST-запрос
    response = authenticated_client.post(
        url
    )  # Используем полноценный Client, вместо APIClient, для полноценной сессии

    # Проверяем статус-код
    assert (
        response.status_code == 302
    ), f"Unexpected status code: {response.status_code}"

    # Убеждаемся, что элемент удален
    assert not CartItem.objects.filter(pk=cart_item.pk).exists()
    assert CartItem.objects.count() == 2
