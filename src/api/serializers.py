from rest_framework import serializers
from store.models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name",)
        swagger_schema_fields = {"example": {"name": "Drama"}}


class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)

    class Meta:
        model = Book
        fields = (
            "title",
            "description",
            "author",
            "price",
            "genre",
            "discounted_price",
        )
        swagger_schema_fields = {
            "example": {
                "title": "Lorem ipsum",
                "description": "Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis",
                "author": "Quisque faucibus",
                "price": 24.99,
                "genre": [{"name": "Drama"}, {"name": "Fiction"}],
                "discounted_price": 19.99,
            }
        }


class BookDetailSerializer(serializers.ModelSerializer):
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
            "is_published",
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
                "is_published": True,
            }
        }
