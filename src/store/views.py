from pyexpat.errors import messages
from random import choice

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch, Q
from django.views import View
from django.views.generic import ListView, DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.contrib.auth.mixins import LoginRequiredMixin

from user_profile.forms import FavoriteBooksForm
from user_profile.models import UserProfile
from .forms import BookSearchForm

from .models import Book, Genre, Quote

from cart.models import Cart, CartItem


class HomePage(ListView):
    model = Book
    template_name = "store/home.html"

    # Загружаем книги с необходимыми данными
    def get_books_with_related_data(self):

        # hasattr для ленивой инициализации, чтобы избежать повторного выполнения запроса к БД
        # Также означает, что данные не загружаются сразу при создании объекта представления, а только в момент, когда они действительно понадобятся.
        if not hasattr(self, "_books_with_related_data"):
            self._books_with_related_data = Book.objects.only(
                "title", "description", "price", "photo", "discounted_price"
            ).prefetch_related(Prefetch("genre", queryset=Genre.objects.only("name")))

        return self._books_with_related_data

    # Получение книг со скидками
    def get_discounted_books(self):
        book_with_related_data = self.get_books_with_related_data()
        return book_with_related_data.filter(discounted_price__isnull=False)

    # Получение случайной книги
    def get_random_book(self):
        books_with_related_data = self.get_books_with_related_data()
        return choice(books_with_related_data)

    # Получение случайной цитаты
    def get_random_quote(self):
        return Quote.objects.order_by("?").only("quote", "author_quote").first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Home"

        context["form"] = form = BookSearchForm(self.request.GET or None)

        # Поиск книг по частичному совпадению с заголовком
        if form.is_valid():
            query = form.cleaned_data["query"]
            if query:
                context["books"] = Book.objects.filter(title__icontaints=query)
            else:
                context["books"] = Book.objects.all()
        # query = self.request.GET.get("query")

        # Не работает так как надо)
        context["pop_books"] = self.get_books_with_related_data
        context["feature_books"] = self.get_books_with_related_data

        context["random_book"] = self.get_random_book()
        context["random_quote"] = self.get_random_quote()

        return context


# @method_decorator(cache_page(60 * 5), name="dispatch")
class BookDetailView(DetailView):
    model = Book
    template_name = "store/book_detail.html"
    context_object_name = "book"
    slug_field = "slug"
    slug_url_kwarg = "book_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object  # Текущая книга

        # Общие данные для книги
        context["title"] = "Book"
        context["old_price"] = book.price if book.discounted_price else None
        context["discounted_price"] = book.discounted_price or book.price

        # Если пользователь авторизован, добавляем данные корзины и избранного
        if self.request.user.is_authenticated:
            try:
                user_profile = self.request.user.userprofile
            except UserProfile.DoesNotExist:
                user_profile = None  # Профиль отсутствует

            if user_profile:
                # Проверка книги в избранных
                context["book_in_favorites"] = user_profile.favorite_books.filter(
                    pk=book.id
                ).exists()

                # Форма для избранных
                context["favorite_books_form"] = FavoriteBooksForm(
                    instance=user_profile, initial={"favorite_books": [book.id]}
                )

            # Получение корзины пользователя
            cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)

            # Проверка книги в корзине
            cart_item = CartItem.objects.filter(cart=cart, book=book).first()
            context["cart"] = cart
            context["cart_item"] = cart_item
            context["in_cart"] = cart_item is not None

        return context


class ToggleFavoriteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, book_slug):
        book = get_object_or_404(Book, slug=book_slug)
        user_profile = request.user.userprofile

        # Добавить или удалить книгу из избранного
        if book in user_profile.favorite_books.all():
            user_profile.favorite_books.remove(book)
        else:
            user_profile.favorite_books.add(book)

        return redirect("book-detail", book_slug=book_slug)


class BookSearchView(View):
    template_name = "store/search_result.html"
    form_class = BookSearchForm

    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", "").strip()
        cache_key = f"search_{query}"

        books = cache.get(cache_key)

        if books is None:
            books = (
                Book.objects.filter(
                    Q(title__icontains=query) | Q(author__icontains=query)
                )
                if query
                else []
            )
            cache.set(cache_key, books, 60 * 5)

        context = {"books": books}
        return render(request, self.template_name, context)


@method_decorator(cache_page(60 * 15), name="dispatch")
class AllBooks(ListView):
    model = Book
    template_name = "store/all_books.html"
    context_object_name = "books"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_key = "all_books"
        books = cache.get(cache_key)

        if not books:
            books = Book.objects.all()
            cache.set(cache_key, books, 60 * 15)

        context["title"] = "All Books"
        context["books"] = books

        return context
