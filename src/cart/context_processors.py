from .utils import get_cart_items_count


def cart_items_count(request):
    """
    Context processor для отображения количества товаров в корзине.
    Добавляет переменную cart_items_count в контекст всех шаблонов.
    """
    return {"cart_items_count": get_cart_items_count(request)}
