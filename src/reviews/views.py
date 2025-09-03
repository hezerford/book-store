from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Review
from store.models import Book


class ReviewListView(ListView):
    template_name = "reviews/list.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        self.book = get_object_or_404(Book, slug=self.kwargs["book_slug"])
        return self.book.reviews.select_related("user").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.book
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ["rating", "text"]
    template_name = "reviews/form.html"

    def get_success_url(self):
        return reverse_lazy(
            "reviews:list", kwargs={"book_slug": self.kwargs["book_slug"]}
        )

    def form_valid(self, form):
        book = get_object_or_404(Book, slug=self.kwargs["book_slug"])
        form.instance.book = book
        form.instance.user = self.request.user
        return super().form_valid(form)


class IsAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        review = self.get_object()
        return review.user_id == self.request.user.id or self.request.user.is_staff


class ReviewUpdateView(LoginRequiredMixin, IsAuthorMixin, UpdateView):
    model = Review
    fields = ["rating", "text"]
    template_name = "reviews/form.html"

    def get_success_url(self):
        return reverse_lazy("reviews:list", kwargs={"book_slug": self.object.book.slug})


class ReviewDeleteView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    model = Review
    template_name = "reviews/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("reviews:list", kwargs={"book_slug": self.object.book.slug})
