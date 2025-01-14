from celery import shared_task
from django.core.mail import send_mail

from core import settings


@shared_task
def send_new_book_email_task(book_title, book_url, email_list):
    """Сообщение получаемое пользователем на почту."""

    subject = f"New Book Added: {book_title}"
    message = f"We've added a new book: {book_title}. Check it out here: {settings.SITE_URL}{book_url}"

    # Отправляем письмо всем подписчикам
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        email_list,
        fail_silently=False,
    )
