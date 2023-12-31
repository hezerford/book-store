from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from shop.models import Book

def user_profile_path(instance, filename):
    return f"profile_pictures/{instance.user.username}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True)
    favorite_books = models.ManyToManyField(Book, related_name='favorited_by', blank=True)

    def __str__(self):
        return self.user.username