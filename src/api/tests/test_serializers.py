import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from store.models import Book, Genre
from reviews.models import Review
from cart.models import Cart, CartItem
from user_profile.models import UserProfile
from api.serializers import (
    GenreSerializer,
    BookSerializer,
    BookDetailSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserProfileSerializer,
)


@pytest.mark.django_db
class TestGenreSerializer:
    def test_genre_serialization(self):
        genre = Genre.objects.create(name="Fiction")
        serializer = GenreSerializer(genre)
        assert serializer.data == {"name": "Fiction"}


@pytest.mark.django_db
class TestBookSerializer:
    def test_basic_book_serialization(self, create_book):
        book = create_book(
            title="Test Book", author="Test Author", price=25.99, discounted_price=19.99
        )
        serializer = BookSerializer(book)
        data = serializer.data

        assert data["title"] == "Test Book"
        assert data["author"] == "Test Author"
        assert data["price"] == "25.99"
        assert data["discounted_price"] == "19.99"
        assert "final_price" in data
        assert "discount_percentage" in data
        assert "is_in_stock" in data
        assert "slug" in data

    def test_computed_fields(self, create_book):
        book = create_book(price=20.00, discounted_price=15.00, stock_quantity=5)
        serializer = BookSerializer(book)
        data = serializer.data

        assert data["final_price"] == 15.00
        assert data["discount_percentage"] == 25.0
        assert data["is_in_stock"] is True


@pytest.mark.django_db
class TestBookDetailSerializer:
    def test_book_detail_fields(self, create_book):
        book = create_book(
            title="Detailed Book",
            description="Long description",
            pages=300,
            publication_year=2023,
        )
        serializer = BookDetailSerializer(book)
        data = serializer.data

        # Проверка присутствия полей
        assert "isbn" in data
        assert "pages" in data
        assert "publication_year" in data
        assert "stock_quantity" in data
        assert data["pages"] == 300
        assert data["publication_year"] == 2023


@pytest.mark.django_db
class TestReviewSerializer:
    def test_review_serialization(self, create_book, authenticated_API_client):
        book = create_book()
        user = authenticated_API_client.user

        review = Review.objects.create(
            book=book, user=user, rating=5, text="Отличная книга!"
        )

        serializer = ReviewSerializer(review)
        data = serializer.data

        assert data["id"] == review.id
        assert data["book"] == book.id
        assert data["book_title"] == book.title
        assert data["user"] == user.username
        assert data["rating"] == 5
        assert data["text"] == "Отличная книга!"

    def test_review_create_auto_assigns_user(
        self, create_book, authenticated_API_client
    ):
        book = create_book()
        user = authenticated_API_client.user

        serializer = ReviewSerializer(
            data={"book": book.id, "rating": 4, "text": "Отличная книга!"},
            context={"request": authenticated_API_client},
        )

        assert serializer.is_valid()
        review = serializer.save()

        assert review.user == user
        assert review.book == book
        assert review.rating == 4

    def test_review_duplicate_prevention(self, create_book, authenticated_API_client):
        """Проверка возможности создания двух отзывов на одну и ту же книгу"""
        book = create_book()
        user = authenticated_API_client.user

        # Создаем первый отзыв
        Review.objects.create(book=book, user=user, rating=5, text="First review")

        # Пытаемся создать второй отзыв для одной и той же книги
        serializer = ReviewSerializer(
            data={"book": book.id, "rating": 3, "text": "Second review"},
            context={"request": authenticated_API_client},
        )

        with pytest.raises(Exception):  # Считываем ошибку
            serializer.is_valid(raise_exception=True)
            serializer.save()


@pytest.mark.django_db
class TestCartSerializers:
    def test_cart_item_serialization(self, create_cart, create_book):
        cart = create_cart()
        book = create_book()
        item = CartItem.objects.create(cart=cart, book=book, quantity=2, price=19.99)

        serializer = CartItemSerializer(item)
        data = serializer.data

        assert data["id"] == item.id
        assert data["book"] == book.id
        assert data["book_title"] == book.title
        assert data["quantity"] == 2
        assert data["price"] == "19.99"
        assert data["total_price"] == 39.98  # 19.99 * 2

    def test_cart_item_create_duplicate_handling(self, create_cart, create_book):
        cart = create_cart()
        book = create_book()

        CartItem.objects.create(cart=cart, book=book, quantity=1, price=20.00)

        serializer = CartItemSerializer(
            data={"book": book.id, "quantity": 2}, context={"cart": cart}
        )

        assert serializer.is_valid()
        item = serializer.save()

        # Should have merged quantities
        assert item.quantity == 3  # 1 + 2
        assert cart.cartitem_set.count() == 1

    def test_cart_serialization_with_items(self, create_cart_with_items):
        cart = create_cart_with_items

        serializer = CartSerializer(cart)
        data = serializer.data

        assert "items" in data
        assert len(data["items"]) == 3
        assert data["total_items"] > 0
        assert data["total_price"] > 0


@pytest.mark.django_db
class TestAuthSerializers:
    def test_user_login_valid_credentials(self, existing_user):
        serializer = UserLoginSerializer(
            data={"username": "testuser", "password": "testpassword"}
        )

        assert serializer.is_valid()
        assert "user" in serializer.validated_data
        assert serializer.validated_data["user"] == existing_user

    def test_user_login_invalid_credentials(self):
        serializer = UserLoginSerializer(
            data={"username": "testuser", "password": "wrongpassword"}
        )

        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_user_register_password_mismatch(self):
        serializer = UserRegisterSerializer(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
                "password_confirm": "different123",
            }
        )

        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_user_register_valid(self):
        serializer = UserRegisterSerializer(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert serializer.is_valid()
        user = serializer.save()

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.check_password("password123")

    def test_user_profile_serialization(self, create_user_profile):
        profile = create_user_profile(first_name="John", last_name="Doe", city="Moscow")

        serializer = UserProfileSerializer(profile)
        data = serializer.data

        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["full_name"] == "John Doe"
        assert data["city"] == "Moscow"
        assert "profile_picture_url" in data
        assert "favorite_books" in data
