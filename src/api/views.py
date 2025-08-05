from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from store.models import Book

from .filters import *
from .serializers import BookSerializer, BookDetailSerializer


class AllBooksAPI(generics.ListAPIView):
    """
    Возвращает список всех доступных книг.

    Включает основную информацию о каждой книге: название, автор, цена, скидочная цена (если есть) и жанры.
    Использует пагинацию.
    """

    queryset = Book.objects.only(
        "title",
        "author",
        "price",
        "discounted_price",
    ).prefetch_related("genre")
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Получить список всех книг",
        description="Возвращает полный список книг с основной информацией. Поддерживает пагинацию.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookDetailAPIView(generics.RetrieveAPIView):
    """
    Предоставляет подробную информацию об отдельной книге.

    Возвращает полную информацию о книге, включая описание, фото и статус публикации.
    """

    queryset = Book.objects.all().prefetch_related("genre")
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Получить детали книги",
        description="Возвращает подробную информацию о книге по её slug или ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DiscountedBookListAPI(generics.ListAPIView):
    """Отображает все книги со скидкой."""

    queryset = Book.objects.filter(discounted_price__isnull=False)
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Получить список книг со скидкой",
        description="Возвращает список книг, у которых указана скидочная цена.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookSearchAPI(generics.ListAPIView):
    """Отображает книгу по запросу или ничего не выводит."""

    queryset = Book.objects.all().prefetch_related("genre")
    serializer_class = BookSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ["price", "title"]

    @extend_schema(
        summary="Поиск и фильтрация книг",
        description="Позволяет искать книги по различным полям и сортировать результаты. Поддерживает фильтрацию через BookFilter и сортировку по цене и названию.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
