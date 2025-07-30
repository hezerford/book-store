from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from store.tasks import send_new_book_email_task

from .models import Book, Subscription


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def clear_book_cache(sender, instance, **kwargs):
    """Удаление всего кэша после добавления/удаления новой книги."""
    from django.core.cache import cache
    from django.core.cache.backends.base import BaseCache

    # Проверяем, есть ли метод delete_pattern
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern("search_*")
        cache.delete("all_books")
    # Альтернатива для DummyCache и других бэкендов без delete_pattern
    elif hasattr(cache, "clear"):
        cache.clear()  # Полная очистка (если доступна)


@receiver(post_save, sender=Book)
def send_new_book_notification(sender, instance, created, **kwargs):
    """Отправка рассылки при добавлении новой книги."""

    if created:  # Только при создании новой книги
        print(f"Signal triggered for book: {instance.title}")
        subscribers = Subscription.objects.filter(is_active=True)
        emails = [subscriber.email for subscriber in subscribers]
        print(f"Sending emails to: {emails}")
        # Запускаем задачу Celery для отправки писем
        send_new_book_email_task.delay(
            instance.title, instance.get_absolute_url(), emails
        )
