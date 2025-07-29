from django.db import models
from django.contrib.auth.models import User

from store.models import Book


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    items = models.ManyToManyField(Book, through="CartItem")

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    # Очистка корзины после заказа
    def clear(self):
        self.items.clear()
        self.is_active = False
        self.save()

    # Привязка корзины к пользователям после входа
    def assign_to_user(self, user):
        self.user = user
        self.session_key = None
        self.save()

    # Получение цены в корзине
    def get_total_price(self):
        return sum(item.price * item.quantity for item in self.cartitem_set.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    class Meta:
        indexes = [
            models.Index(fields=["session_key"]),
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.book.discounted_price or self.book.price
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("cart", "book")
