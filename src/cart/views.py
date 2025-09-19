from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .utils import add_to_cart, get_or_create_cart
from .models import CartItem


class CartView(TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_or_create_cart(self.request)
        # Оставляем старый cart_items для обратной совместимости
        cart_items_with_subtotal = []
        for item in cart.cartitem_set.select_related("book").all():
            cart_items_with_subtotal.append(
                {"cartitem": item, "subtotal": float(item.price * item.quantity)}
            )

        context["cart_items_with_subtotal"] = cart_items_with_subtotal

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


@method_decorator(csrf_exempt, name="dispatch")
class UpdateCartItemView(View):
    """AJAX представление для обновления количества товара в корзине"""

    def post(self, request, book_slug):
        try:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, book__slug=book_slug)

            # Получаем новое количество
            new_quantity = request.POST.get("quantity")
            action = request.POST.get("action")  # 'plus', 'minus', или None

            if action == "plus":
                new_quantity = cart_item.quantity + 1
            elif action == "minus":
                new_quantity = cart_item.quantity - 1
            elif new_quantity:
                try:
                    new_quantity = int(new_quantity)
                except ValueError:
                    return JsonResponse(
                        {"success": False, "error": "Некорректное количество"},
                        status=400,
                    )
            else:
                return JsonResponse(
                    {"success": False, "error": "Не указаны данные для обновления"},
                    status=400,
                )

            # Валидация количества
            if new_quantity <= 0:
                cart_item.delete()
                return JsonResponse(
                    {
                        "success": True,
                        "removed": True,
                        "message": "Товар удалён из корзины",
                        "cart_total": cart.get_total_price(),
                        "cart_items_count": cart.get_total_items(),
                    }
                )

            # Обновляем количество
            cart_item.quantity = new_quantity
            cart_item.save()

            # Пересчитываем итоги корзины
            cart.total_price = cart.get_total_price()
            cart.total_items = cart.get_total_items()
            cart.save(update_fields=["total_price", "total_items"])

            return JsonResponse(
                {
                    "success": True,
                    "quantity": cart_item.quantity,
                    "item_subtotal": float(cart_item.price * cart_item.quantity),
                    "cart_total": float(cart.get_total_price()),
                    "cart_items_count": cart.get_total_items(),
                }
            )

        except CartItem.MultipleObjectsReturned:
            return JsonResponse(
                {"success": False, "error": "Найдено несколько товаров с таким slug"},
                status=400,
            )
        except CartItem.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Товар не найден в корзине"}, status=404
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
