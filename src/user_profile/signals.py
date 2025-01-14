from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete

from .models import UserProfile


@receiver(post_delete, sender=UserProfile)
def delete_profile_picture(sender, instance, **kwargs):
    """Удаление из файловой системы фото пользователя при сбросе/смене аватара."""

    if instance.profile_picture:
        default_storage.delete(instance.profile_picture.path)
