import pytest
from datetime import date
from user_profile.models import UserProfile, user_profile_path
from mixer.backend.django import mixer


@pytest.mark.django_db
def test_userprofile(existing_user, create_user_profile):
    user_profile = create_user_profile()
    assert (
        str(user_profile) == existing_user.username
    ), "__str__ does not return the correct username."


@pytest.mark.django_db
def test_userprofile_with_data(existing_user):
    user_profile = mixer.blend(UserProfile, user=existing_user)

    # Проверяем, что пользователь профиля совпадает с существующим пользователем
    assert (
        user_profile.user == existing_user
    ), "User is not correctly assigned to UserProfile."

    # Проверяем, что поля профиля не пустые, если это критично для логики
    for field in [
        "first_name",
        "last_name",
        "street",
        "city",
        "postal_code",
        "country",
        "bio",
        "profile_picture",
    ]:
        value = getattr(user_profile, field, None)
        assert value is not None, f"Field {field} is None, expected a value."


@pytest.mark.django_db
def test_userprofile_names(create_user_profile):
    user_profile = create_user_profile(first_name="John", last_name="Doe")

    assert user_profile.first_name == "John"
    assert user_profile.last_name == "Doe"
    assert (
        user_profile.full_name() == "John Doe"
    ), "full_name method does not return the correct format."


@pytest.mark.django_db
def test_userprofile_picture_path(existing_user, create_user_profile):
    user_profile = create_user_profile()
    path = user_profile_path(user_profile, "example.jpg")
    assert (
        path == f"profile_pictures/{existing_user.username}/example.jpg"
    ), "Profile picture path is incorrect."


@pytest.mark.django_db
def test_userprofile_favorite_books(create_user_profile, create_book):
    user_profile = create_user_profile()
    book1 = create_book(title="Book 1")
    book2 = create_book(title="Book 2")

    user_profile.favorite_books.add(book1, book2)

    assert book1 in user_profile.favorite_books.all()
    assert book2 in user_profile.favorite_books.all()

    user_profile.favorite_books.remove(book1)
    assert book1 not in user_profile.favorite_books.all()
    assert book2 in user_profile.favorite_books.all()


@pytest.mark.django_db
def test_userprofile_birth_date(create_user_profile):
    user_profile = create_user_profile(birth_date=date(1990, 1, 1))
    assert user_profile.birth_date == date(1990, 1, 1)
