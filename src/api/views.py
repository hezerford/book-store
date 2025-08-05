from django_filters import rest_framework as filters

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from store.models import Book

from .filters import *
from .serializers import BookSerializer, BookDetailSerializer


class AllBooksAPI(generics.ListAPIView):
    queryset = Book.objects.only(
        "title",
        "author",
        "price",
        "discounted_price",
    ).prefetch_related("genre")
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookDetailAPIView(generics.RetrieveAPIView):
    queryset = Book.objects.filter(discounted_price__isnull=False).prefetch_related(
        "genre",
    )
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DiscountedBookListAPI(generics.ListAPIView):
    """Отображает все книги со скидкой."""

    queryset = Book.objects.filter(discounted_price__isnull=False)
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookSearchAPI(generics.ListAPIView):
    """Отображает книгу по запросу или ничего не выводит."""

    queryset = Book.objects.all().prefetch_related("genre")
    serializer_class = BookSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter
    ordering_fields = ["price", "title"]
