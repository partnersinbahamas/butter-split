import pytest
from typing import Callable
from django.urls import reverse_lazy

from service.models import Currency, Event, User, Participant
from service.tests.fixtures import get_currency

RAW_PARTICIPANTS = ['Participant-1', 'Participant-2']

@pytest.fixture()
def get_currency_to_update(db) -> Currency:
    return Currency.objects.create(
        code='EUR',
        name='Euro',
        symbol='€',
    )

@pytest.fixture()
def update_post_data(db, get_currency_to_update: Currency) -> dict:
    return {
        'name': 'Test event update',
        'currency': get_currency_to_update.pk,
        'participants': ['Participant-1', 'Participant-3'],
    }

@pytest.fixture()
def create_event(db, get_currency) -> Callable:
    def index(session_key: str = None, owner: User = None) -> Event:
        event = Event.objects.create(
            name="Test event",
            currency=get_currency,
            owner=owner,
            session_id=session_key,
        )

        participants = Participant.objects.bulk_create([
            Participant(name=participant, creator=owner)
            for participant in RAW_PARTICIPANTS
        ])
        event.participants.set(participants)

        return event

    return index

@pytest.mark.django_db
class TestPrivateEventUpdateView:
    def test_event_should_be_updated_if_user_authenticated(
            self,
            client,
            django_user_model,
            update_post_data: dict,
            create_event: Callable,
            get_currency_to_update: Callable,
    ):
        user = django_user_model.objects.create_user(
            username="Test user",
            password="test-user-password"
        )
        client.force_login(user)

        event = create_event(owner=user)

        url = reverse_lazy('service:event-update', kwargs={'pk': event.pk})
        response = client.post(url, data=update_post_data)

        event.refresh_from_db()

        event_participants_names = [
            participant.name
            for participant in event.participants.all()
        ]

        assert response.status_code == 302
        assert event.name == update_post_data['name']
        assert event.currency == get_currency_to_update
        assert event_participants_names == update_post_data['participants']


class TestPublicEventUpdateView:
    def test_event_should_be_updated_with_session_key(
            self,
            client,
            update_post_data: dict,
            create_event: Callable,
            get_currency_to_update: Callable,
    ):
        session = client.session
        session.save()

        event = create_event(session_key=session.session_key)

        url = reverse_lazy('service:event-update', kwargs={'pk': event.pk})
        response = client.post(url, data=update_post_data)

        event.refresh_from_db()

        event_participants_names = [
            participant.name
            for participant in event.participants.all()
        ]

        assert response.status_code == 302
        assert event.name == update_post_data['name']
        assert event.currency == get_currency_to_update
        assert event_participants_names == update_post_data['participants']
