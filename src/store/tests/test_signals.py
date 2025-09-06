import pytest
from unittest.mock import patch
from django.core.cache import cache
from store.models import Book, Subscription
from django.db import transaction


@pytest.mark.django_db
def test_clear_book_cache_signal(create_book):
    # Устанавливаем значения в кэш
    cache.set("all_books", "cached_books")

    # Для тестов проверяем только конкретные ключи, которые точно очищаются
    cache.set("search_specific_test", "cached_search")

    # Убедимся, что кэш установлен
    assert cache.get("search_specific_test") == "cached_search"
    assert cache.get("all_books") == "cached_books"

    # Создаем книгу, чтобы вызвать сигнал
    book = create_book()

    # Удаляем книгу, чтобы вызвать сигнал post_delete
    book.delete()

    # Проверяем, что конкретные ключи очищены
    # (только те, которые мы точно знаем, что будут очищены)
    assert cache.get("all_books") is None, "All books cache was not cleared."

    # Для search ключей проверяем только те, которые мы установили конкретно
    assert cache.get("search_specific_test") is None, "Search cache was not cleared."


@pytest.mark.django_db
@patch("store.tasks.send_new_book_notification_task.delay")
def test_send_new_book_notification_signal(
    mock_send_task, create_subscription, create_book
):
    # Создаем подписчиков c коммитом в БД
    with transaction.atomic():
        create_subscription(email="user1@example.com")
        create_subscription(email="user2@example.com", is_active=False)
        create_subscription(email="user3@example.com")

    # Убедитесь, что подписчики действительно существуют
    assert Subscription.objects.count() == 3, "Subscriptions were not created."

    # Создаем книгу
    book = create_book(title="New Book")

    # Проверяем, что задача Celery вызвана ровно один раз с ID книги
    mock_send_task.assert_called_once_with(book.pk)
