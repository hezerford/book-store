from django.contrib import admin
from .models import Book, Genre, Quote, Email


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "author",
        "price",
        "discounted_price",
        "photo",
        "is_published",
    )
    filter_vertical = ("genre",)
    search_fields = ("title", "content")
    list_editable = ("is_published",)
    list_filter = ("is_published", "time_create")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("quote", "author_quote")
    search_fields = ("quote", "author_quote")


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("email", "date_subscribed", "is_active", "last_sent")
