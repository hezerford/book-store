from django import forms
from profiles.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "address", "phone_number", "profile_picture")
        exclude = ('favorite_books',)

class FavoriteBooksForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['favorite_books']