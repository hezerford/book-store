from django.contrib import admin
from .models import CartItem, Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "session_key",
        "items",
        "created_at",
        "updated_at",
        "is_active",
    )
    filter_horizontal = ("items",)
    list_editable = ("is_active",)
    list_filter = ("created_at", "updated_at", "is_active")
    search_fields = ("user", "session_key")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "book", "quantity", "price")
