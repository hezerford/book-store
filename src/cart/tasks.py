from celery import shared_task


@shared_task
def delete_old_anonymous_carts():
    from cart.models import Cart  # Импорт модели внутри задачи
    from datetime import timedelta
    from django.utils.timezone import now

    threshold_date = now() - timedelta(days=1)
    deleted_count, _ = Cart.objects.filter(
        user=None,
        session_key__isnull=False,
        is_active=True,
        created_at__lt=threshold_date,
    ).delete()

    return f"{deleted_count} old anonymous carts deleted"
