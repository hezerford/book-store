import django_filters
from store.models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    author = django_filters.CharFilter(lookup_expr="icontains")
    genre = django_filters.CharFilter(field_name="genre__name", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["title", "author", "genre"]
