import pytest
from datetime import date

from user_profile.forms import UserProfileForm
from user_profile.models import UserProfile


@pytest.mark.django_db
def test_user_profile_form_valid_data(create_user_profile):
    user_profile = create_user_profile()
    form_data = {
        "first_name": "John",
        "last_name": "Doe",
        "street": "123 Main St",
        "city": "Springfield",
        "postal_code": "12345",
        "country": "USA",
        "birth_date": date(2000, 1, 1),
        "bio": "This is a test bio.",
        "phone_number": "+1234567890",
    }

    form = UserProfileForm(data=form_data, instance=user_profile)
    assert form.is_valid(), "Form should be valid with correct data."
    saved_profile = form.save()
    assert saved_profile.first_name == "John"
    assert saved_profile.city == "Springfield"


@pytest.mark.parametrize(
    "birth_date, expected_error",
    [
        (date(1800, 1, 1), "Пожалуйста, укажите настоящую дату рождения."),
        (None, None),  # Отсутствие ошибки, если дата не указана
    ],
)
def test_user_profile_form_invalid_birth_date(birth_date, expected_error):
    form_data = {"birth_date": birth_date}
    form = UserProfileForm(data=form_data)

    if expected_error:
        assert not form.is_valid(), "Form should be invalid for old birth_date."
        assert expected_error in form.errors["birth_date"]
    else:
        assert form.is_valid(), "Form should be valid with no birth_date."


@pytest.mark.parametrize(
    "postal_code, expected_error",
    [
        ("12345", None),  # Валидный почтовый индекс
        ("12 345", "Почтовый индекс должен содержать только буквы и цифры."),
        ("!@#$%", "Почтовый индекс должен содержать только буквы и цифры."),
    ],
)
def test_user_profile_form_invalid_postal_code(postal_code, expected_error):
    form_data = {"postal_code": postal_code}
    form = UserProfileForm(data=form_data)

    if expected_error:
        assert not form.is_valid(), "Form should be invalid for invalid postal_code."
        assert expected_error in form.errors["postal_code"]
    else:
        assert form.is_valid(), "Form should be valid with correct postal_code."


@pytest.mark.parametrize(
    "phone_number, expected_error",
    [
        ("+1234567890", None),  # Валидный номер телефона
        (
            "12345",
            "Пожалуйста, введите действительный номер телефона, состоящий не менее чем из 10 цифр.",
        ),
        ("", None),  # Пустой номер допустим
    ],
)
def test_user_profile_form_invalid_phone_number(phone_number, expected_error):
    form_data = {"phone_number": phone_number}
    form = UserProfileForm(data=form_data)

    if expected_error:
        assert not form.is_valid(), "Form should be invalid for short phone_number."
        assert expected_error in form.errors["phone_number"]
    else:
        assert form.is_valid(), "Form should be valid with correct phone_number."
