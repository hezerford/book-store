from django.urls import path
from .views import (
    HomePage,
    BookDetailView,
    ToggleFavoriteView,
    BookSearchView,
    AllBooks,
    UnsubscribeView,
)

urlpatterns = [
    path("", HomePage.as_view(), name="home"),
    path("search/", BookSearchView.as_view(), name="book-search"),
    path("book/<slug:book_slug>/", BookDetailView.as_view(), name="book-detail"),
    path(
        "book/<slug:book_slug>/add-to-favorites/",
        ToggleFavoriteView.as_view(),
        name="add-to-favorites",
    ),
    path(
        "book/<slug:book_slug>/remove-from-favorites/",
        ToggleFavoriteView.as_view(),
        name="remove-from-favorites",
    ),
    path("books/", AllBooks.as_view(), name="all-books"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
]
