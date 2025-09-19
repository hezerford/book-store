from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, UpdateCartItemView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("add-to-cart/<slug:book_slug>/", AddToCartView.as_view(), name="add-to-cart"),
    path(
        "remove-from-cart/<slug:book_slug>/",
        RemoveFromCartView.as_view(),
        name="remove-from-cart",
    ),
    path(
        "update-item/<slug:book_slug>/",
        UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),
]
