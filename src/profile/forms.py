from django import forms
from django.core.exceptions import ValidationError

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "street",
            "city",
            "postal_code",
            "country",
            "birth_date",
            "bio",
            "phone_number",
            "profile_picture",
        ]

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if birth_date and birth_date.year < 1900:
            raise ValidationError("Пожалуйста, укажите настоящую дату рождения.")
        return birth_date

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if postal_code and not postal_code.isalnum():
            raise ValidationError(
                "Почтовый индекс должен содержать только буквы и цифры."
            )
        return postal_code

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and len(phone_number) < 10:
            raise ValidationError(
                "Пожалуйста, введите действительный номер телефона, состоящий не менее чем из 10 цифр."
            )
        return phone_number


class FavoriteBooksForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["favorite_books"]
