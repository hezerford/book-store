from django.urls import path
from .views import AllBooksAPI, DiscountedBookListView, BookSearchAPI, BookDetailAPIView

urlpatterns = [
    path("all-books/", AllBooksAPI.as_view(), name="all-books-api"),
    path(
        "discounted-books/",
        DiscountedBookListView.as_view(),
        name="discounted-books-api",
    ),
    path("book-search/", BookSearchAPI.as_view(), name="book-search-api"),
    path("books/<int:pk>/", BookDetailAPIView.as_view(), name="book-detail-api"),
]
