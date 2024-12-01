from random import choice

from django.shortcuts import render
from django.db.models import Prefetch
from django.views.generic import ListView, DetailView

from .forms import BookSearchForm

from .models import Book, Genre, Quote

class HomePage(ListView):
    model = Book
    template_name = 'store/home.html'

    # Загружаем книги с необходимыми данными
    def get_books_with_related_data(self):

        # hasattr для ленивой инциализации, чтобы избежать повторного выполнения запроса к БД
        # Также означает, что данные не загружаются сразу при создании объекта представления, а только в момент, когда они действительно понадобятся.
        if not hasattr(self, "_books_with_related_data"):
            self._books_with_related_data = Book.objects.only(
                "title", "description", "price", "photo", "discounted_price"
            ).prefetch_related(
                Prefetch('genre', queryset=Genre.objects.only("name"))
            )

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
        return Quote.objects.order_by('?').only("quote", "author_quote").first()

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

