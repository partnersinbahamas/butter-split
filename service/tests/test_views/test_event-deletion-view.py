import pytest
from django.urls import reverse_lazy

from service.models import Event
from service.tests.fixtures import get_currency


@pytest.mark.django_db
class TestPrivateEventDeleteView:
    def test_event_should_be_deleted_for_authenticated_user(self, client, django_user_model, get_currency):
        user = django_user_model.objects.create_user(
            username='test-user',
            password='test-user-password'
        )

        client.force_login(user)

        event = Event.objects.create(
            name='test-event',
            owner=user,
            currency=get_currency
        )

        url = reverse_lazy('service:event-delete', kwargs={'pk': event.pk})
        response = client.post(url)

        assert response.status_code == 302 # redirect to confirmation
        assert not Event.objects.filter(pk=event.pk).exists()


@pytest.mark.django_db
class TestPublicEventDeleteView:
    def test_event_should_be_deleted_with_session_user(self, client, get_currency):
        session = client.session
        session.save()

        event = Event.objects.create(
            name='test-event',
            session_id=session.session_key,
            currency=get_currency
        )

        url = reverse_lazy('service:event-delete', kwargs={'pk': event.pk})
        response = client.post(url)

        assert response.status_code == 302  # redirect to confirmation
        assert not Event.objects.filter(pk=event.pk).exists()
