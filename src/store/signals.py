from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Book


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def clear_book_cache(sender, isntance, **kwargs):
    from django.core.cache import cache

    cache.delete_pattern("search_*")
