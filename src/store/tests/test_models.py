from datetime import datetime
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from store.models import Book, Subscription, Genre, Quote

from io import BytesIO
from PIL import Image


@pytest.mark.django_db
class TestGenre:
    def test_genre_creation(self):
        genre = Genre.objects.create(name="Fiction", description="Fictional books")

        assert genre.name == "Fiction"
        assert genre.description == "Fictional books"
        assert str(genre) == "Fiction"


@pytest.mark.django_db
class TestBook:
    def test_book_creation(self):
        genre = Genre.objects.create(name="Adventure")
        book = Book.objects.create(
            title="Test Book",
            description="Description",
            author="Author name",
            price=19.99,
            is_published=True,
        )
        book.genre.add(genre)

        assert book.title == "Test Book"
        assert book.description == "Description"
        assert book.author == "Author name"
        assert float(book.price) == 19.99
        assert book.is_published is True
        assert genre in book.genre.all()
        assert str(book) == "Test Book"
        assert book.get_absolute_url() == f"/book/{book.slug}/"

    def test_book_slug_generation(self):
        book = Book.objects.create(
            title="Test Slug Book",
            description="Description",
            author="Author",
            price=10.99,
        )

        assert book.slug == "test-slug-book"

    def test_book_image_upload(self, create_book):
        # Загружаем тестовое изображение
        buffer = BytesIO()
        Image.new("RGB", (10, 10), color="red").save(buffer, format="JPEG")
        buffer.seek(0)

        uploaded_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=buffer.getvalue(),
            content_type="image/jpeg",
        )

        # Создаем книгу с изображением
        book = create_book(
            photo=uploaded_image,
        )

        # Проверяем, что изображение загружено
        assert book.photo, "Image was not uploaded"

        # Проверяем путь загрузки изображения
        today = datetime.now()
        expected_path = (
            f"book_covers/{today.year}/{today.month:02d}/{today.day:02d}/test_image.jpg"
        )
        assert (
            book.photo.name == expected_path
        ), f"Unexpected image path: {book.photo.name}"


@pytest.mark.django_db
class TestQuote:
    def test_quote_creation(self):
        quote = Quote.objects.create(
            quote="To be or not to be",
            author_quote="William Shakespeare",
            source="Hamlet",
        )

        assert quote.quote == "To be or not to be"
        assert quote.author_quote == "William Shakespeare"
        assert quote.source == "Hamlet"
        assert str(quote) == "William Shakespeare: To be or not to be..."


@pytest.mark.django_db
class TestEmail:
    def test_email_unique(self):
        Subscription.objects.create(email="unique@example.com")
        with pytest.raises(Exception):
            Subscription.objects.create(email="unique@example.com")
