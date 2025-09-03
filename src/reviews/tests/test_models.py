import pytest
from django.contrib.auth.models import User

from store.models import Book, Genre
from reviews.models import Review


@pytest.mark.django_db
def test_review_unique_per_user_book():
    user = User.objects.create_user(username="u1", password="p")
    genre = Genre.objects.create(name="Test")
    book = Book.objects.create(title="B", description="D", author="A", price=10)
    book.genre.add(genre)

    Review.objects.create(book=book, user=user, rating=5)
    with pytest.raises(Exception):
        Review.objects.create(book=book, user=user, rating=4)
