import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from reviews.models import Review


@pytest.mark.django_db
class TestReviewCRUD:
    def test_create_review_authenticated(
        self, authenticated_client, existing_user, create_book
    ):
        book = create_book(slug="book-for-create-review")
        url = reverse("book-detail", kwargs={"book_slug": book.slug})

        response = authenticated_client.post(
            url,
            data={"action": "create_review", "rating": 5, "text": "Great book!"},
        )

        assert response.status_code == 302
        assert (
            Review.objects.filter(book=book, user=existing_user).count() == 1
        ), "Review was not created"

    def test_create_review_unauthenticated(self, client, create_book):
        book = create_book(slug="book-for-unauth-create")
        url = reverse("book-detail", kwargs={"book_slug": book.slug})

        response = client.post(
            url, data={"action": "create_review", "rating": 4, "text": "ok"}
        )

        assert response.status_code == 302
        assert reverse("login") in response.url
        assert Review.objects.filter(book=book).count() == 0

    def test_delete_review_by_author(
        self, authenticated_client, existing_user, create_book
    ):
        book = create_book(slug="book-for-delete")
        review = Review.objects.create(
            book=book, user=existing_user, rating=4, text="x"
        )

        url = reverse("book-detail", kwargs={"book_slug": book.slug})
        response = authenticated_client.post(
            url, data={"action": "delete_review", "review_id": review.id}
        )

        assert response.status_code == 302
        assert not Review.objects.filter(id=review.id).exists()

    def test_delete_review_by_non_author_denied(
        self, authenticated_client, existing_user, create_book
    ):
        other_user = User.objects.create_user(username="other", password="p")
        book = create_book(slug="book-for-denied-delete")
        review = Review.objects.create(book=book, user=other_user, rating=3, text="y")

        url = reverse("book-detail", kwargs={"book_slug": book.slug})
        response = authenticated_client.post(
            url, data={"action": "delete_review", "review_id": review.id}
        )

        assert response.status_code == 302
        assert Review.objects.filter(
            id=review.id
        ).exists(), "Non-author should not delete"


@pytest.mark.django_db
def test_reviews_pagination(client, create_book):
    book = create_book(slug="book-for-pagination")
    # Создаем 12 пользователей и 12 отзывов и проверяем пагинацию
    for i in range(12):
        user = User.objects.create_user(username=f"u{i}", password="p")
        Review.objects.create(book=book, user=user, rating=5, text=f"r{i}")

    url = reverse("book-detail", kwargs={"book_slug": book.slug})

    # Страница 1
    resp1 = client.get(url)
    assert resp1.status_code == 200
    assert "reviews" in resp1.context
    assert len(resp1.context["reviews"]) == 10

    # Страница 2
    resp2 = client.get(url, {"reviews_page": 2})
    assert resp2.status_code == 200
    assert len(resp2.context["reviews"]) == 2
