from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing
from django.urls import reverse


@shared_task
def send_new_book_notification_task(book_id: int) -> int:
    """Готовит список подписчиков и шлёт уведомление о новой книге.
    Возвращает количество адресов для отправки.
    """
    from store.models import Book, Subscription

    book = Book.objects.filter(pk=book_id).first()
    if not book:
        return 0

    subscribers = Subscription.objects.filter(is_active=True).values_list(
        "email", flat=True
    )
    count = 0

    subject = f"New Book Added: {book.title}"
    base_message = f"We've added a new book: {book.title}. Check it out here: {settings.SITE_URL}{book.get_absolute_url()}"

    for email in subscribers:
        token = signing.dumps(email, salt="unsubscribe")
        unsubscribe_link = f"{settings.SITE_URL}{reverse('unsubscribe')}?={token}"
        message = f"{base_message}\n\nTo unsubscribe: {unsubscribe_link}"
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False
        )
        count += 1

    return count
