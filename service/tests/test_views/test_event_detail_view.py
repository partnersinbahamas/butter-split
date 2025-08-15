import pytest
from typing import Callable
from django.urls import reverse_lazy

from service.models import Participant, Currency, Event, User


RAW_PARTICIPANTS = ['Participant-1', 'Participant-2']

@pytest.fixture()
def get_currency(db) -> Currency:
    return Currency.objects.create(
        code='USD',
        name='US Dollar',
        symbol='$',
    )

@pytest.fixture()
def create_event(db, get_currency) -> Callable:
    def index(owner: User = None) -> Event:
        event = Event.objects.create(
            name="Test event",
            currency=get_currency,
            owner=owner,
        )

        participants = Participant.objects.bulk_create([
            Participant(name=participant, creator=owner)
            for participant in RAW_PARTICIPANTS
        ])
        event.participants.set(participants)

        return event

    return index

class TestEventDetailView:
    def test_event_detail_view_should_display_event_data(self, client, django_user_model, create_event, get_currency):
        user = django_user_model.objects.create_user(username='test-user', password='test-user-password')
        event = create_event(user)

        client.force_login(user)

        url = reverse_lazy('service:event-detail', kwargs={'pk': event.pk})

        response = client.get(url)

        assert RAW_PARTICIPANTS[0] in response.content.decode()
        assert RAW_PARTICIPANTS[1] in response.content.decode()

        assert event.name in response.content.decode()
        assert event.currency.symbol in response.content.decode()

