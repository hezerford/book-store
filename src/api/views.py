from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from store.models import Book, Genre

from .filters import *
from .serializers import BookSerializer, BookDetailSerializer, GenreSerializer

from django.views.decorators.cache import cache_page


@method_decorator(cache_page(60 * 5), name="dispatch")
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

    @extend_schema(
        tags=["Books"],
        summary="Получить список всех книг",
        description="Возвращает полный список книг с основной информацией. Поддерживает пагинацию.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BookDetailAPIView(generics.RetrieveAPIView):
    """
    Предоставляет подробную информацию об отдельной книге.

    Возвращает полную информацию о книге, включая описание, фото и статус публикации.
    """

    queryset = Book.objects.filter(is_published=True).prefetch_related("genre")
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    @extend_schema(
        tags=["Books"],
        summary="Получить детали книги",
        description="Возвращает подробную информацию о книге по её slug или ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@method_decorator(cache_page(60 * 3), name="dispatch")
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

    @extend_schema(
        tags=["Books"],
        summary="Получить список книг со скидкой",
        description="Возвращает список книг, у которых указана скидочная цена.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 3), name="dispatch")
class BookSearchAPI(generics.ListAPIView):
    """Отображает книгу по запросу или ничего не выводит."""

    queryset = Book.objects.filter(is_published=True).prefetch_related("genre")
    serializer_class = BookSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ["price", "title"]

    @extend_schema(
        tags=["Books"],
        summary="Поиск и фильтрация книг",
        description="Позволяет искать книги по различным полям и сортировать результаты. Поддерживает фильтрацию через BookFilter и сортировку по цене и названию.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
class GenreListAPI(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=["Books"],
        summary="Получить список всех жанров",
        description="Возвращает полный список доступных жанров книг.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@method_decorator(cache_page(60 * 10), name="dispatch")
class BooksByGenreAPI(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=["Books"],
        summary="Получить книги по жанру",
        description="Возвращает список книг определенного жанра.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        genre_id = self.kwargs["genre_id"]
        return Book.objects.filter(
            genre__id=genre_id, is_published=True
        ).prefetch_related("genre")
