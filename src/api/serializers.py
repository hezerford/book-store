from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from store.models import Book, Genre
from cart.models import Cart, CartItem
from reviews.models import Review
from user_profile.models import UserProfile


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


# ===== REVIEWS SERIALIZERS =====


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book_title = serializers.ReadOnlyField(source="book.title")

    class Meta:
        model = Review
        fields = (
            "id",
            "book",
            "book_title",
            "user",
            "rating",
            "text",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "user")
        swagger_schema_fields = {
            "example": {
                "id": 1,
                "book": 5,
                "book_title": "Преступление и наказание",
                "user": "johndoe",
                "rating": 5,
                "text": "Отличная книга, рекомендую всем!",
                "created_at": "2023-09-15T10:30:00Z",
                "updated_at": "2023-09-15T10:30:00Z",
            }
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReviewDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book_title = serializers.ReadOnlyField(source="book.title")

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "user", "book")
        swagger_schema_fields = {
            "example": {
                "id": 1,
                "book": 5,
                "book_title": "Преступление и наказание",
                "user": "johndoe",
                "rating": 5,
                "text": "Отличная книга, рекомендую всем! Захватывающий сюжет и глубокий психологизм.",
                "created_at": "2023-09-15T10:30:00Z",
                "updated_at": "2023-09-15T14:20:00Z",
            }
        }


# ===== CART SERIALIZERS =====


class CartItemSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source="book.title")
    book_slug = serializers.ReadOnlyField(source="book.slug")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "book",
            "book_title",
            "book_slug",
            "quantity",
            "price",
            "total_price",
        )
        read_only_fields = ("price", "total_price")
        swagger_schema_fields = {
            "example": {
                "id": 1,
                "book": 5,
                "book_title": "Преступление и наказание",
                "book_slug": "prestuplenie-i-nakazanie",
                "quantity": 2,
                "price": 24.99,
                "total_price": 49.98,
            }
        }

    def get_total_price(self, obj):
        return obj.price * obj.quantity

    def create(self, validated_data):
        cart = self.context["cart"]
        book = validated_data["book"]

        # Проверка на существование книги в корзине
        existing_item = CartItem.objects.filter(cart=cart, book=book).first()
        if existing_item:
            existing_item.quantity += validated_data.get("quantity", 1)
            existing_item.save()
            return existing_item

        validated_data["cart"] = cart
        validated_data["price"] = book.get_final_price()
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cartitem_set", many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "total_price",
            "total_items",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "user",
            "total_price",
            "total_items",
            "created_at",
            "updated_at",
        )
        swagger_schema_fields = {
            "example": {
                "id": 1,
                "user": 2,
                "total_price": 99.95,
                "total_items": 3,
                "items": [
                    {
                        "id": 1,
                        "book": 5,
                        "book_title": "Преступление и наказание",
                        "book_slug": "prestuplenie-i-nakazanie",
                        "quantity": 2,
                        "price": 24.99,
                        "total_price": 49.98,
                    },
                    {
                        "id": 2,
                        "book": 8,
                        "book_title": "Война и мир",
                        "book_slug": "vojna-i-mir",
                        "quantity": 1,
                        "price": 49.97,
                        "total_price": 49.97,
                    },
                ],
                "created_at": "2023-09-15T10:00:00Z",
                "updated_at": "2023-09-15T14:30:00Z",
            }
        }


# ===== AUTHENTICATION SERIALIZERS =====


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        swagger_schema_fields = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123",
            }
        }

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(_("Invalid credentials"))
            if not user.is_active:
                raise serializers.ValidationError(_("User account is disabled"))
            data["user"] = user
        else:
            raise serializers.ValidationError(_("Must include username and password"))

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password_confirm",
        )
        swagger_schema_fields = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "password_confirm": "securepassword123",
            }
        }

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "first_name",
            "last_name",
            "full_name",
            "street",
            "city",
            "postal_code",
            "country",
            "birth_date",
            "bio",
            "phone_number",
            "profile_picture",
            "profile_picture_url",
            "date_joined",
            "is_active",
            "favorite_books",
        )
        read_only_fields = ("user", "date_joined")
        swagger_schema_fields = {
            "example": {
                "user": 2,
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "street": "123 Main St",
                "city": "Moscow",
                "postal_code": "101000",
                "country": "Russia",
                "birth_date": "1990-05-15",
                "bio": "Book lover and avid reader",
                "phone_number": "+7-999-123-45-67",
                "profile_picture": None,
                "profile_picture_url": None,
                "date_joined": "2023-01-15T08:30:00Z",
                "is_active": True,
                "favorite_books": [5, 8, 12],
            }
        }

    def get_full_name(self, obj):
        return obj.full_name()

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def update(self, instance, validated_data):
        # Handle favorite_books as many-to-many
        favorite_books = validated_data.pop("favorite_books", None)
        if favorite_books is not None:
            instance.favorite_books.set(favorite_books)

        return super().update(instance, validated_data)
