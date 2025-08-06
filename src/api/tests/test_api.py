import pytest
from django.urls import reverse
from rest_framework import status


def assert_book_fields(book_data):
    assert "title" in book_data
    assert "description" in book_data
    assert "author" in book_data
    assert "genre" in book_data
    assert "price" in book_data


@pytest.mark.django_db
def test_all_books_api(authenticated_API_client, create_three_books):
    # Создаем экземпляры книг
    create_three_books()

    url = reverse("all-books-api")
    response = authenticated_API_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    # Проверить, что response.data - это словарь
    assert isinstance(response.data, dict)

    # Проверить ключи пагинации
    assert "count" in response.data
    assert "results" in response.data

    # Проверить, что "results" содержит данные
    results = response.data["results"]
    assert len(results) == 3  # Проверяем длину списка в "results"

    # Проверка наличия пагинации
    assert response.data["next"] is None
    assert response.data["previous"] is None

    first_book = results[0]
    assert_book_fields(first_book)


@pytest.mark.django_db
def test_book_detail_api(authenticated_API_client, create_book):
    book = create_book()
    url = reverse("book-detail-api", kwargs={"slug": book.slug})
    response = authenticated_API_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    assert_book_fields(response.data)


@pytest.mark.django_db
def test_discounted_book_list_api(authenticated_API_client, create_book):
    create_book(discounted_price=None)
    create_book(discounted_price=15)
    create_book(discounted_price=20)

    url = reverse("discounted-books-api")
    response = authenticated_API_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    assert isinstance(response.data, dict)

    results = response.data["results"]
    assert len(results) == 2  # Проверяем количество книг в results

    # Проверка наличия пагинации
    assert response.data["next"] is None
    assert response.data["previous"] is None


@pytest.mark.django_db(transaction=True)
def test_book_search_api(authenticated_API_client, create_book):
    create_book(
        title="Python Book",
        description="Learn Python programming",
        author="Python Author",
        price=20.0,
        discounted_price=15.0,
        slug="python-book",
    )
    create_book(
        title="Django Book",
        description="Building web applications with Django",
        author="Django Author",
        price=14.0,
        discounted_price=12.0,
        is_published=True,
        slug="django-book",
    )
    create_book(
        title="Java Book",
        description="Introduction to Java programming",
        author="Java Author",
        price=10.0,
        is_published=True,
        slug="java-book",
    )

    url = reverse("book-search-api")
    response = authenticated_API_client.get(url, {"title": "Python"})
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что в ответе есть данные и они соответствуют ожидаемой структуре
    assert isinstance(response.data, dict)
    assert (
        response.data["count"] == 1
    )  # Ожидаем только одну книгу с соответствующим заголовком

    book = response.data["results"][0]

    assert "Learn Python programming" in book["description"]
    assert "Python Author" in book["author"]
