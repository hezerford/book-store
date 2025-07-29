from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CartItem


@receiver([post_save, post_delete], sender=CartItem)
def update_cart_totals(sender, instance, **kwargs):
    cart = instance.cart
    cart.total_price = cart.get_total_price()
    cart.total_items = cart.get_total_items()
    cart.save(update_fields=["total_price", "total_items"])
