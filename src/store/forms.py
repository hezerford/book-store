from django import forms
from .models import Subscription


class BookSearchForm(forms.Form):
    query = forms.CharField(
        label="",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Book name"}),
    )


class SubscriptionForm(forms.ModelForm):
    """Форма заполнения подписки на рассылку."""

    class Meta:
        model = Subscription
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Subscription.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже подписан.")
        return email
