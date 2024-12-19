from django import forms


class BookSearchForm(forms.Form):
    query = forms.CharField(
        label="",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Book name"}),
    )
