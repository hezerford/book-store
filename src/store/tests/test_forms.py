import pytest
from store.forms import BookSearchForm


def test_book_search_form_valid_data():
    form = BookSearchForm(data={"query": "Python Programming."})
    assert form.is_valid(), "Form should be valid for a valid query."


def test_book_search_form_empty_data():
    form = BookSearchForm(data={"query": ""})
    assert form.is_valid(), "Form should be valid for an empty query."


def test_book_search_form_exceeds_max_length():
    long_query = "a" * 101
    form = BookSearchForm(data={"query": long_query})
    assert (
        not form.is_valid()
    ), "Form should not be valid for query exceeding max_length."


def test_book_search_form_widget_placeholder():
    form = BookSearchForm()
    placeholder = form.fields["query"].widget.attrs.get("placeholder", "")
    assert placeholder == "Book name", "Placeholder is not set correctly."
