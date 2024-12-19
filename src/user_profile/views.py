from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User


from .forms import UserProfileForm
from .models import UserProfile


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "profile/profile-detail.html"
    context_object_name = "user_profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs["username"]

        user = get_object_or_404(User, username=username)
        user_profile = (
            UserProfile.objects.select_related("user")
            .prefetch_related("favorite_books")
            .get(user=user)
        )

        context["user_profile"] = user_profile

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = "profile/profile-update.html"
    context_object_name = "user_profile"
    form_class = UserProfileForm

    # Возвращаем профиль текущего пользователя
    def get_object(self, queryset=None):
        return self.request.user.userprofile

    # Проверяем, что текущий пользователь обновляет только свой профиль
    def dispatch(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if user_profile.user != request.user:
            messages.error(
                request, "You are not allowed to update another user's profile."
            )
            return redirect("profile-detail", username=request.user.username)

        # Если всё ок, продолжаем выполнение
        return super().dispatch(request, *args, **kwargs)

    # Определяем URL, куда перенаправлен будет пользователь после успешного обновления профиля
    def get_success_url(self):
        return reverse(
            "profile-detail", kwargs={"username": self.request.user.username}
        )

    def form_valid(self, form):
        profile_picture = self.request.FILES.get("profile_picture")
        if profile_picture:
            self.object.profile_picture = profile_picture

        if "reset_profile_picture" in self.request.POST:
            user_profile = self.request.user.userprofile
            if user_profile.profile_picture:
                # Удалить фотографию профиля и установить значение profile_picture в None
                user_profile.profile_picture.delete()
                user_profile.profile_picture = None
                user_profile.save()  # Сохраняем модель профиля

        return super().form_valid(form)
