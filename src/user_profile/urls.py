from django.urls import path
from .views import ProfileDetailView, ProfileUpdateView

urlpatterns = [
    path("<str:username>", ProfileDetailView.as_view(), name="profile-detail"),
    path(
        "edit/<str:username>",
        ProfileUpdateView.as_view(),
        name="profile-update",
    ),
]
