from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "country",
        "bio",
        "date_joined",
        "phone_number",
        "is_active",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "country",
        "date_joined",
    )
