import pytest
from django.urls import reverse
from django.core import signing

from store.models import Subscription


@pytest.mark.django_db
def test_unsubscribe_via_valid_token(client, create_subscription):
    sub = create_subscription(email="u@example.com", is_active=True)
    token = signing.dumps(sub.email, salt="unsubscribe")
    url = reverse("unsubscribe") + f"?t={token}"

    response = client.get(url)

    assert response.status_code in (302, 301)
    sub.refresh_from_db()
    assert sub.is_active is False


@pytest.mark.django_db
def test_unsubscribe_via_invalid_token(client, create_subscription):
    sub = create_subscription(email="u2@example.com", is_active=True)
    url = reverse("unsubscribe") + "?t=invalid-token"

    response = client.get(url)

    assert response.status_code in (302, 301)
    sub.refresh_from_db()
    assert sub.is_active is True
