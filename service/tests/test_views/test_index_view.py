from typing import Callable

import pytest
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from service.models import Currency, Event
from service.tests.fixtures import get_currency


@pytest.fixture()
def create_events(db, get_currency):
    def index(
            session_key: str = None,
            owner: get_user_model = None
    ) -> list[Event]:
        return [
            Event.objects.create(
                name=f"event-{i+1}",
                currency=get_currency,
                session_id=session_key,
                owner=owner
            )
            for i in range(4)
        ]

    return index


@pytest.mark.django_db
class TestPublicIndexView:
    def test_index_view_with_session_key(
            self,
            client,
            get_currency,
            create_events: Callable):
        session = client.session
        session.save()

        create_events(session_key=session.session_key)

        url = reverse_lazy('service:index')
        response = client.get(url)

        assert 'Sign in' in response.content.decode()
        assert 'event-4' in response.content.decode()
        assert 'event-3' in response.content.decode()
        assert 'event-2' in response.content.decode()
        assert 'event-1' not in response.content.decode()


@pytest.mark.django_db
class TestPrivateIndexView:
    def test_index_view_for_authenticated_user(
            self,
            client,
            create_events,
            django_user_model,
            get_currency: Currency
    ):
        user = django_user_model.objects.create_user(
            username="test",
            password="user-password"
        )

        client.force_login(user)
        create_events(owner=user)

        url = reverse_lazy('service:index')
        response = client.get(url)

        assert response.status_code == 200
        assert 'event-4' in response.content.decode()
        assert 'event-3' in response.content.decode()
        assert 'event-2' in response.content.decode()
        assert 'event-1' not in response.content.decode()
        assert user.username in response.content.decode()
