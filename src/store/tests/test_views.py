from django.test import override_settings
import pytest
from django.urls import reverse
from mixer.backend.django import mixer

from store.models import Book, Genre, Quote
from user_profile.models import UserProfile


@pytest.mark.django_db
def test_homepage_view(client, create_three_books):
    create_three_books()
    url = reverse("home")

    response = client.get(url)

    assert response.status_code == 200, "HomePage did not return 200 OK."
    assert "random_book" in response.context, "Random book not included in context."
    assert "random_quote" in response.context, "Random quote not included in context."


@pytest.mark.django_db
def test_homepage_random_book(client, create_three_books):
    create_three_books()
    url = reverse("home")
    response = client.get(url)

    random_book = response.context["random_book"]
    assert random_book is not None, "Random book was not selected."


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)  # Отключаем кэш во время теста, чтобы не возникало ошибок
@pytest.mark.django_db
def test_book_detail_view(client, create_book):
    book = create_book(title="Test Book", slug="test-book")
    url = reverse("book-detail", kwargs={"book_slug": book.slug})

    response = client.get(url)

    assert response.status_code == 200, "BookDetailView did not return 200 OK."
    assert (
        response.context["book"] == book
    ), "BookDetailView did not pass correct book to context."


@pytest.mark.django_db
def test_toggle_favorite_view(authenticated_client, create_book, existing_user):
    # Проверка добавления книги в избранное
    book = create_book(slug="test-book")
    user_profile = existing_user.userprofile

    url = reverse("add-to-favorites", kwargs={"book_slug": book.slug})
    response = authenticated_client.post(url)

    assert response.status_code == 302, "ToggleFavoriteView did not redirect."
    assert book in user_profile.favorite_books.all(), "Book was not added to favorites."

    # Проверка удаления книги из избранного

    url = reverse("remove-from-favorites", kwargs={"book_slug": book.slug})
    response = authenticated_client.post(url)

    assert response.status_code == 302, "ToggleFavoriteView did not redirect."
    assert (
        book not in user_profile.favorite_books.all()
    ), "Book was not removed from favorites."


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)  # Отключаем кэш во время теста, чтобы не возникало ошибок
@pytest.mark.django_db
def test_all_books_view(client, create_three_books):
    create_three_books()
    url = reverse("all-books")

    response = client.get(url)

    assert response.status_code == 200, "AllBooks did not return 200 OK."
    assert (
        len(response.context["books"]) == 3
    ), "AllBooks context does not contain correct number of books."


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)  # Отключаем кэш во время теста, чтобы не возникало ошибок
@pytest.mark.parametrize(
    "query, expected_count, expected_titles",
    [
        ("Python", 1, ["Python Programming"]),
        ("Django", 0, []),
        ("", 0, []),
    ],
)
@pytest.mark.django_db
def test_book_search_view(client, create_book, query, expected_count, expected_titles):
    create_book(title="Python Programming")
    url = reverse("book-search")
    response = client.get(url, {"query": query})

    assert response.status_code == 200
    books = response.context["books"]
    assert len(books) == expected_count
    assert all(book.title in expected_titles for book in books)
