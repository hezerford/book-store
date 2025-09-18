from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from store.models import Book, Genre
from cart.models import Cart, CartItem
from reviews.models import Review
from user_profile.models import UserProfile

from .filters import *
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    GenreSerializer,
    ReviewSerializer,
    ReviewDetailSerializer,
    CartSerializer,
    CartItemSerializer,
    UserProfileSerializer,
)

from django.views.decorators.cache import cache_page


@method_decorator(cache_page(60 * 5), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Получить список всех книг",
    description="Возвращает полный список книг с основной информацией. Поддерживает пагинацию.",
)
class AllBooksAPI(generics.ListAPIView):
    """
    Возвращает список всех доступных книг.

    Включает основную информацию о каждой книге: название, автор, цена, скидочная цена (если есть) и жанры.
    Использует пагинацию.
    """

    queryset = (
        Book.objects.filter(is_published=True)
        .only(
            "title",
            "description",
            "author",
            "price",
            "discounted_price",
        )
        .prefetch_related("genre")
    )
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = ["title", "author", "genre"]
    ordering_fields = ["price", "title"]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 15), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Получить детали книги",
    description="Возвращает подробную информацию о книге по её slug или ID.",
)
class BookDetailAPIView(generics.RetrieveAPIView):
    """
    Предоставляет подробную информацию об отдельной книге.

    Возвращает полную информацию о книге, включая описание, фото и статус публикации.
    """

    queryset = Book.objects.filter(is_published=True).prefetch_related("genre")
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@method_decorator(cache_page(60 * 3), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Получить список книг со скидкой",
    description="Возвращает список книг, у которых указана скидочная цена.",
)
class DiscountedBookListAPI(generics.ListAPIView):
    """Отображает все книги со скидкой."""

    queryset = (
        Book.objects.filter(discounted_price__isnull=False, is_published=True)
        .only(
            "title",
            "author",
            "price",
            "discounted_price",
        )
        .prefetch_related("genre")
    )
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ["price", "title"]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 3), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Поиск и фильтрация книг",
    description="Позволяет искать книги по различным полям и сортировать результаты. Поддерживает фильтрацию через BookFilter и сортировку по цене и названию.",
)
class BookSearchAPI(generics.ListAPIView):
    """Отображает книгу по запросу или ничего не выводит."""

    queryset = Book.objects.filter(is_published=True).prefetch_related("genre")
    serializer_class = BookSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ["price", "title"]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Получить список всех жанров",
    description="Возвращает полный список доступных жанров книг.",
)
class GenreListAPI(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 10), name="dispatch")
@extend_schema(
    tags=["Books"],
    methods=["GET"],
    summary="Получить книги по жанру",
    description="Возвращает список книг определенного жанра.",
)
class BooksByGenreAPI(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        genre_id = self.kwargs["genre_id"]
        return Book.objects.filter(
            genre__id=genre_id, is_published=True
        ).prefetch_related("genre")


# Вспомогательная функция для создания или получения корзины пользователя
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# ===== REVIEWS VIEWS =====


@extend_schema(
    tags=["Reviews"],
    methods=["GET"],
    summary="Получить отзывы о книге",
    description="Возвращает список всех отзывов для конкретной книги.",
)
@extend_schema(
    tags=["Reviews"],
    methods=["POST"],
    summary="Добавить отзыв",
    description="Добавляет новый отзыв к книге.",
)
class ReviewsByBookAPI(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        book_id = self.kwargs["book_id"]
        return Review.objects.filter(book_id=book_id)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(
    tags=["Reviews Detail"],
    methods=["GET"],
    summary="Получить отзыв",
    description="Возвращает детальную информацию об отзыве.",
)
@extend_schema(
    tags=["Reviews Detail"],
    methods=["PUT"],
    summary="Полностью обновить отзыв",
    description="Полностью обновляет содержимое отзыва.",
)
@extend_schema(
    tags=["Reviews Detail"],
    methods=["PUT", "PATCH"],
    summary="Частично обновить отзыв",
    description="Частично обновляет содержимое отзыва.",
)
@extend_schema(
    tags=["Reviews Detail"],
    methods=["DELETE"],
    summary="Удалить отзыв",
    description="Удаляет отзыв пользователя.",
)
class ReviewDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ===== CART VIEWS =====


@extend_schema(
    tags=["Cart"],
    summary="Получить содержимое корзины",
    description="Возвращает все товары в корзине пользователя.",
)
class CartAPI(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_or_create_cart(self.request.user)


@extend_schema(
    tags=["Cart"],
    methods=["GET"],
    summary="Получить товары в корзине",
    description="Возвращает список всех товаров в корзине пользователя с количеством и ценой.",
)
@extend_schema(
    tags=["Cart"],
    methods=["POST"],
    summary="Добавить товар в корзину",
    description="Добавляет новый товар в корзину пользователя. Если товар уже есть, увеличивает количество.",
)
class CartItemListCreate(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["cart"] = get_or_create_cart(self.request.user)
        return context


@extend_schema(
    tags=["Cart Detail"],
    methods=["GET"],
    summary="Получить товар из корзины",
    description="Возвращает детальную информацию о конкретном товаре в корзине.",
)
@extend_schema(
    tags=["Cart Detail"],
    methods=["PUT"],
    summary="Полностью обновить товар в корзине",
    description="Заменяет все данные товара в корзине.",
)
@extend_schema(
    tags=["Cart Detail"],
    methods=["PATCH"],
    summary="Обновить товар в корзине",
    description="Обновляет количество товара в корзине или другие параметры.",
)
@extend_schema(
    tags=["Cart Detail"],
    methods=["DELETE"],
    summary="Удалить товар из корзины",
    description="Удаляет товар из корзины пользователя.",
)
class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ===== USER PROFILE VIEWS =====


@extend_schema(
    tags=["User Profile"],
    methods=["GET"],
    summary="Получить профиль пользователя",
    description="Возвращает полную информацию профиля пользователя.",
)
@extend_schema(
    tags=["User Profile"],
    methods=["PATCH"],
    summary="Обновить профиль пользователя частично",
    description="Позволяет частично изменить данные профиля пользователя.",
)
@extend_schema(
    tags=["User Profile"],
    methods=["PUT"],
    summary="Обновить профиль пользователя",
    description="Позволяет полностью изменить данные профиля пользователя.",
)
class UserProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
