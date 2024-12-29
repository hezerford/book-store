from django.db import models
from django.contrib.auth.models import User

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

from store.models import Book


def user_profile_path(instance, filename):
    return f"profile_pictures/{instance.user.username}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True)

    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,15}$",
        message="Пожалуйста, введите действительный номер телефона, состоящий не менее чем из 10 цифр.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )  # Validators should be a list

    profile_picture = models.ImageField(
        upload_to=user_profile_path, blank=True, null=True
    )

    is_active = models.BooleanField(default=True)

    favorite_books = models.ManyToManyField(
        Book, related_name="favorited_by", blank=True
    )

    def __str__(self):
        return self.user.username

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
