from django.urls import path
from .views import AllBooksAPI, DiscountedBookListAPI, BookSearchAPI, BookDetailAPIView

urlpatterns = [
    path("all-books/", AllBooksAPI.as_view(), name="all-books-api"),
    path(
        "discounted-books/",
        DiscountedBookListAPI.as_view(),
        name="discounted-books-api",
    ),
    path("book-search/", BookSearchAPI.as_view(), name="book-search-api"),
    path("books/<slug:slug>/", BookDetailAPIView.as_view(), name="book-detail-api"),
]
