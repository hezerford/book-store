import pytest
from datetime import timedelta
from django.utils.timezone import now
from cart.models import Cart
from cart.tasks import delete_old_anonymous_carts


@pytest.mark.django_db
class TestDeleteCart:
    def test_delete_old_anonymous_carts(self, db, create_cart):
        """Проверяет, что старая корзина анонимного пользователя удаляется."""
        old_cart = create_cart(created_at=now() - timedelta(days=2), is_active=True)
        recent_cart = create_cart(created_at=now(), is_active=True)

        assert Cart.objects.count() == 2

        result = delete_old_anonymous_carts()

        assert Cart.objects.count() == 1
        assert not Cart.objects.filter(id=old_cart.id).exists()
        assert Cart.objects.filter(id=recent_cart.id).exists()

        # Проверяем сообщение результата задачи
        assert result == "1 old anonymous carts deleted"

    def test_no_carts_to_delete(self, db, create_cart):
        """Проверяет, что задача ничего не удаляет, если нет старых корзин."""
        # Создаём только недавние корзины
        create_cart(created_at=now(), is_active=True)
        create_cart(created_at=now(), is_active=True)

        # Проверяем начальное количество корзин
        assert Cart.objects.count() == 2

        # Запускаем задачу
        result = delete_old_anonymous_carts()

        # Проверяем, что корзины остались
        assert Cart.objects.count() == 2
        assert result == "0 old anonymous carts deleted"
