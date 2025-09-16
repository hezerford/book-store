import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_search_json_returns_results(client, create_book):
    create_book(
        title="Birds Gonna Be Happy",
        author="Sanchit Howdy",
        slug="birds-gonna-be-happy",
    )
    create_book(title="Consectetur adipiscing", author="Placerat")

    url = reverse("book-search")
    response = client.get(url, {"format": "json", "query": "Birds"})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    titles = [item["title"] for item in data["results"]]
    assert "Birds Gonna Be Happy" in titles


@pytest.mark.django_db
def test_search_json_empty_query(client):
    url = reverse("book-search")
    response = client.get(url, {"format": "json", "query": ""})

    assert response.status_code == 200
    data = response.json()
    assert data == {"results": []}


@pytest.mark.django_db
def test_search_html_view_lists_books(client, create_book):
    b1 = create_book(title="Python 101")
    create_book(title="Django Guide")

    url = reverse("book-search")
    response = client.get(url, {"query": "Python"})

    assert response.status_code == 200
    # HTML-ветка рендерит шаблон с контекстом
    assert "books" in response.context
    books = response.context["books"]
    assert len(books) == 1
    assert books[0].title == "Python 101"


@pytest.mark.django_db
def test_search_html_empty_query_returns_empty_list(client):
    url = reverse("book-search")
    response = client.get(url, {"query": ""})

    assert response.status_code == 200
    assert "books" in response.context
    assert list(response.context["books"]) == []
