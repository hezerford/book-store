from rest_framework import serializers
from store.models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name",)
        swagger_schema_fields = {"example": {"name": "Drama"}}


class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "title",
            "description",
            "author",
            "price",
            "genre",
            "discounted_price",
            "final_price",
            "discount_percentage",
            "is_in_stock",
            "slug",
        )
        swagger_schema_fields = {
            "example": {
                "title": "Lorem ipsum",
                "description": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis",
                "author": "Quisque faucibus",
                "price": 24.99,
                "genre": [{"name": "Drama"}, {"name": "Fiction"}],
                "discounted_price": 19.99,
                "final_price": 19.99,
                "discount_percentage": 20.0,
                "is_in_stock": True,
                "slug": "lorem-ipsum",
            }
        }

    def get_final_price(self, obj):
        return obj.get_final_price()

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()


class BookDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "title",
            "description",
            "author",
            "genre",
            "photo",
            "price",
            "discounted_price",
            "final_price",
            "discount_percentage",
            "is_in_stock",
            "is_published",
            "isbn",
            "pages",
            "publication_year",
            "stock_quantity",
            "slug",
        )
        swagger_schema_fields = {
            "example": {
                "title": "Lorem ipsum",
                "description": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis",
                "author": "Quisque faucibus",
                "genre": [{"name": "Drama"}, {"name": "Fiction"}],
                "photo": "/static/img/default-book.png",
                "price": 24.99,
                "discounted_price": 19.99,
                "final_price": 19.99,
                "discount_percentage": 20.0,
                "is_in_stock": True,
                "is_published": True,
                "isbn": "978-0-123456-47-2",
                "pages": 320,
                "publication_year": 2023,
                "stock_quantity": 15,
                "slug": "lorem-ipsum",
            }
        }

    def get_final_price(self, obj):
        return obj.get_final_price()

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()
