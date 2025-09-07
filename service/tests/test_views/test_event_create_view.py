import pytest
from django.urls import reverse_lazy

from service.models import Currency, Participant, Event
from service.tests.fixtures import get_currency

@pytest.fixture()
def get_post_data(get_currency: Currency):
    return {
        'name': 'Test user event creation',
        'currency': get_currency.pk,
        'participants': ['Participant-1'],
    }

@pytest.mark.django_db
class TestPrivateEventCreateView:
    def test_event_should_not_be_created_if_form_invalid(self, client, django_user_model, get_post_data):
        user = django_user_model.objects.create_user(
            username='test-user',
            password='user-password'
        )

        client.force_login(user)

        post_data = get_post_data.copy()
        # invalid name
        post_data['name'] = ''

        url = reverse_lazy('service:event-create')

        client.post(url, data=post_data)

        assert Event.objects.count() == 0
        assert Participant.objects.count() == 0

    def test_event_create_view_with_user(
            self,
            client,
            django_user_model,
            get_currency: Currency,
            get_post_data: dict,
    ):
        user = django_user_model.objects.create_user(
            username='test-user',
            password='user-password'
        )

        client.force_login(user)

        url = reverse_lazy('service:event-create')

        client.post(url, data=get_post_data)

        created_event = Event.objects.get(name=get_post_data['name'])
        created_participant = Participant.objects.get(name=get_post_data['participants'][0])

        assert Event.objects.count() == 1
        assert Participant.objects.count() == 1

        assert created_event.name == get_post_data['name']
        assert created_event.currency == get_currency
        assert created_event.participants.count() == 1
        assert created_participant.name == get_post_data['participants'][0]
        assert created_event in created_participant.events.all()
        assert created_event.session_id is None


@pytest.mark.django_db
class TestPublicEventCreateView:
    def test_event_should_not_be_created_if_form_invalid(self, client, get_post_data):
        session = client.session
        session.save()

        post_data = get_post_data.copy()
        # invalid name
        post_data['name'] = ''

        url = reverse_lazy('service:event-create')

        client.post(url, data=post_data)

        assert Event.objects.count() == 0
        assert Participant.objects.count() == 0

    def test_event_create_with_session_key(self, client, get_post_data, get_currency):
        session = client.session
        session.save()

        url = reverse_lazy('service:event-create')
        client.post(url, data=get_post_data)

        created_event = Event.objects.get(name=get_post_data['name'])
        created_participant = Participant.objects.get(name=get_post_data['participants'][0])

        assert Event.objects.count() == 1
        assert Participant.objects.count() == 1

        assert created_event.name == get_post_data['name']
        assert created_event.currency == get_currency
        assert created_event.participants.count() == 1
        assert created_participant.name == get_post_data['participants'][0]
        assert created_event in created_participant.events.all()
        assert created_event.session_id == session.session_key
        assert created_event.owner is None
