from django.urls import path
from .views import (
    AllBooksAPI,
    DiscountedBookListAPI,
    BookSearchAPI,
    BookDetailAPIView,
    GenreListAPI,
    BooksByGenreAPI,
    ReviewsByBookAPI,
    ReviewDetailAPI,
    CartAPI,
    CartItemListCreate,
    CartItemDetail,
    UserProfileAPI,
)

urlpatterns = [
    path("all-books/", AllBooksAPI.as_view(), name="all-books-api"),
    path(
        "discounted-books/",
        DiscountedBookListAPI.as_view(),
        name="discounted-books-api",
    ),
    path("book-search/", BookSearchAPI.as_view(), name="book-search-api"),
    path("books/<slug:slug>/", BookDetailAPIView.as_view(), name="book-detail-api"),
    # Additional book-related endpoints
    path("genres/", GenreListAPI.as_view(), name="genre-list-api"),
    path(
        "genres/<int:genre_id>/books/",
        BooksByGenreAPI.as_view(),
        name="books-by-genre-api",
    ),
    # Reviews endpoints
    path(
        "books/<int:book_id>/reviews/",
        ReviewsByBookAPI.as_view(),
        name="reviews-by-book",
    ),
    path("reviews/<int:pk>/", ReviewDetailAPI.as_view(), name="review-detail"),
    # Cart endpoints
    path("cart/", CartAPI.as_view(), name="api_cart"),
    path("cart/items/", CartItemListCreate.as_view(), name="cart-items"),
    path("cart/items/<int:pk>/", CartItemDetail.as_view(), name="cart-item-detail"),
    # User profile endpoint
    path("profile/", UserProfileAPI.as_view(), name="user-profile"),
]
