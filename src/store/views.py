from django.contrib import messages
from random import choice

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Count, Prefetch, Q
from django.views import View
from django.views.generic import ListView, DetailView

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.contrib.auth.mixins import LoginRequiredMixin

from user_profile.forms import FavoriteBooksForm
from user_profile.models import UserProfile
from .forms import BookSearchForm, SubscriptionForm

from .models import Book, Genre, Quote, Subscription

from cart.models import Cart, CartItem

from reviews.forms import ReviewForm
from reviews.models import Review

from django.core import signing

from django_ratelimit.decorators import ratelimit


class HomePage(ListView):
    model = Book
    template_name = "store/home.html"
    form_class = SubscriptionForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        return redirect("home")

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

        # Создаём экземпляр формы вручную
        context["form"] = BookSearchForm(self.request.GET or None)
        context["subscription_form"] = self.form_class()

        # Поиск книг по частичному совпадению с заголовком
        form = context["form"]
        if form.is_valid():
            query = form.cleaned_data["query"]
            if query:
                context["books"] = Book.objects.filter(title__icontains=query)
            else:
                context["books"] = Book.objects.all()

        context["pop_books"] = self.get_books_with_related_data()
        context["feature_books"] = self.get_books_with_related_data()
        context["random_book"] = self.get_random_book()
        context["random_quote"] = self.get_random_quote()

        return context


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

        # Отзывы книги
        reviews_qs = book.reviews.select_related("user").order_by("-created_at")

        page_number = self.request.GET.get(
            "reviews_page"
        )  # направляет на ?reviews_page=2
        paginator = Paginator(reviews_qs, 10)  # 10 отзывов на странице
        reviews_page = paginator.get_page(page_number)  # получаем безопасно страницу

        context["reviews_page"] = reviews_page  # объект страницы
        context["reviews"] = reviews_page.object_list  # элементы текущей страницы

        # Текущий отзыв пользователя и форма
        user_review = None
        if self.request.user.is_authenticated:
            user_review = Review.objects.filter(
                book=book, user=self.request.user
            ).first()
        context["user_review"] = user_review
        context["review_form"] = (
            ReviewForm()
            if self.request.user.is_authenticated and not user_review
            else None
        )

        # Средний рейтинг книги и количества отзывов
        agg = book.reviews.aggregate(avg=Avg("rating"), cnt=Count("id"))
        context["avg_rating"] = round(agg["avg"] or 0, 1)
        context["reviews_count"] = agg["cnt"] or 0

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        book = self.object
        action = request.POST.get("action")

        if not request.user.is_authenticated:
            messages.error(request, "Нужно войти, чтобы оставить отзыв.")
            return redirect("login")

        if action == "create_review":
            if Review.objects.filter(book=book, user=request.user).exists():
                messages.warning(request, "Вы уже оставили отзыв на эту книгу.")
            else:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    Review.objects.create(
                        book=book,
                        user=request.user,
                        rating=form.cleaned_data["rating"],
                        text=form.cleaned_data.get("text", ""),
                    )
                    messages.success(request, "Отзыв добавлен.")
                else:
                    messages.error(request, "Проверьте корректность формы отзыва.")

        elif action == "delete_review":
            review_id = request.POST.get("review_id")
            review = Review.objects.filter(
                id=review_id, book=book, user=request.user
            ).first()
            if review:
                review.delete()
                messages.success(request, "Отзыв удалён.")
            else:
                messages.error(request, "Отзыв не найден или у вас нет прав.")

        return redirect("book-detail", book_slug=book.slug)


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
    """Отображение всех книг."""

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


@method_decorator(
    ratelimit(key="ip", rate="10/5m", method="POST", block=True), name="post"
)
class SubscribeToMailing(View):
    """Подписка на рассылку."""

    def get(self, request):
        # Отображение формы подписки
        form = SubscriptionForm()
        return render(request, "store/home.html", {"form": form})

    def post(self, request):
        # Обработка формы подписки
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вы успешно подписались на рассылку!")
        else:
            messages.error(request, "Произошла ошибка. Проверьте введенные данные.")
        return redirect("home")


class UnsubscribeView(View):
    http_method_names = ["get"]

    def get(self, request):
        token = request.GET.get("t")
        try:
            email = signing.loads(token, salt="unsubscribe", max_age=7 * 24 * 3600)
        except (signing.BadSignature, signing.SignatureExpired):
            messages.error(request, "Invalid or expired unsubscribe link.")
            return redirect("home")

        Subscription.objects.filter(email=email).update(is_active=False)
        messages.success(request, "You have been unsubscribed.")
        return redirect("home")
