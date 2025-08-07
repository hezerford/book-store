import django_filters
from decimal import Decimal
from store.models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    author = django_filters.CharFilter(lookup_expr="icontains")
    genre = django_filters.CharFilter(field_name="genre__name", lookup_expr="icontains")

    # Фильтры по цене
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Фильтр по наличию скидки
    has_discount = django_filters.BooleanFilter(
        method="filter_has_discount", label="Только со скидкой"
    )

    # Фильтр по наличию на складе
    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock", label="Только в наличии"
    )

    # Фильтр по году издания
    publication_year = django_filters.NumberFilter(field_name="publication_year")
    min_year = django_filters.NumberFilter(
        field_name="publication_year", lookup_expr="gte"
    )
    max_year = django_filters.NumberFilter(
        field_name="publication_year", lookup_expr="lte"
    )

    # Фильтр по количеству страниц
    min_pages = django_filters.NumberFilter(field_name="pages", lookup_expr="gte")
    max_pages = django_filters.NumberFilter(field_name="pages", lookup_expr="lte")

    # Фильтр по ISBN
    isbn = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "genre",
            "min_price",
            "max_price",
            "has_discount",
            "in_stock",
            "publication_year",
            "min_year",
            "max_year",
            "min_pages",
            "max_pages",
            "isbn",
        ]

    def filter_has_discount(self, queryset, name, value):
        """Фильтр для книг со скидкой"""
        if value:
            return queryset.filter(discounted_price__isnull=False)
        return queryset

    def filter_in_stock(self, queryset, name, value):
        """Фильтр для книг в наличии"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset
