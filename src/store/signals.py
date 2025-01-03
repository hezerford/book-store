from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from store.tasks import send_new_book_email_task

from .models import Book, Subscription


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def clear_book_cache(sender, instance, **kwargs):
    from django.core.cache import cache

    cache.delete_pattern("search_*")  # Удаляем все ключи, начинающиеся с "search_"
    cache.delete("all_books")


@receiver(post_save, sender=Book)
def send_new_book_notification(sender, instance, created, **kwargs):
    if created:  # Только при создании новой книги
        print(f"Signal triggered for book: {instance.title}")
        subscribers = Subscription.objects.filter(is_active=True)
        emails = [subscriber.email for subscriber in subscribers]
        print(f"Sending emails to: {emails}")
        # Запускаем задачу Celery для отправки писем
        send_new_book_email_task.delay(
            instance.title, instance.get_absolute_url(), emails
        )
