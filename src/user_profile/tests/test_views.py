import pytest
from django.urls import reverse

from user_profile.models import UserProfile

from django.contrib.auth.models import User


@pytest.mark.django_db
def test_profile_detail_view(authenticated_client, create_user_profile):
    user_profile = create_user_profile(first_name="John", last_name="Doe")

    url = reverse("profile-detail", kwargs={"username": user_profile.user.username})
    response = authenticated_client.get(url)

    assert response.status_code == 200, "ProfileDetailView did not return 200 OK."
    assert "user_profile" in response.context, "User profile not in context."
    assert (
        response.context["user_profile"] == user_profile
    ), "Incorrect user profile in context."


@pytest.mark.django_db
def test_profile_update_view(authenticated_client, create_user_profile):
    user_profile = create_user_profile(first_name="John", last_name="Doe")
    url = reverse("profile-update", kwargs={"username": user_profile.user.username})

    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "street": "123 Main St",
        "city": "Springfield",
        "postal_code": "12345",
        "country": "USA",
    }
    response = authenticated_client.post(url, data)

    assert (
        response.status_code == 302
    ), "ProfileUpdateView did not redirect after update."
    user_profile.refresh_from_db()
    assert user_profile.first_name == "Jane", "First name was not updated."
    assert user_profile.city == "Springfield", "City was not updated."


@pytest.mark.django_db
def test_profile_update_view_reset_picture(authenticated_client, create_user_profile):
    user_profile = create_user_profile(profile_picture="profile.jpg")
    url = reverse("profile-update", kwargs={"username": user_profile.user.username})

    response = authenticated_client.post(url, data={"reset_profile_picture": "1"})

    user_profile.refresh_from_db()
    assert (
        response.status_code == 302
    ), "ProfileUpdateView did not redirect after reset."
    assert not user_profile.profile_picture, "Profile picture was not reset."


@pytest.mark.django_db
def test_profile_update_view_access_other_user_profile(
    authenticated_client, create_user_profile
):
    user_profile = create_user_profile(first_name="John", last_name="Doe")
    other_user = User.objects.create(username="other_user", password="other_pass12345")
    other_user_profile = UserProfile.objects.create(user=other_user)

    url = reverse(
        "profile-update", kwargs={"username": other_user_profile.user.username}
    )
    response = authenticated_client.post(url)

    assert (
        response.status_code == 302
    ), "Unauthorized access to another profile not redirected."
    assert response.url == reverse(
        "profile-detail", kwargs={"username": user_profile.user.username}
    ), "Unauthorized user not redirected to their profile."


@pytest.mark.django_db
def test_profile_detail_view_redirect_unauthenticated(client, create_user_profile):
    user_profile = create_user_profile()

    url = reverse("profile-detail", kwargs={"username": user_profile.user.username})
    response = client.get(url)

    assert response.status_code == 302, "Unauthenticated user was not redirected."
    assert (
        "/login/" in response.url
    ), "Unauthenticated user was not redirected to login."
