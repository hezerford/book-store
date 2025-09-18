from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .utils import add_to_cart, get_or_create_cart
from .models import CartItem


class CartView(TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_or_create_cart(self.request)
        context["cart_items"] = cart.cartitem_set.select_related("book").all()
        context["total_price"] = cart.get_total_price()
        context["total_items"] = cart.get_total_items()

        return context


class AddToCartView(View):
    def post(self, request, book_slug):
        # Добавляет книгу в корзину
        return add_to_cart(request, book_slug)


class RemoveFromCartView(View):
    def post(self, request, book_slug):
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, book__slug=book_slug)
        cart_item.delete()
        return redirect("cart")
