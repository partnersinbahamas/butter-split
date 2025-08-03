import pytest
from django.db.models import QuerySet
from django.urls import reverse_lazy

from service.models import Currency, User, Event

CREATED_EVENTS_COUNT = 10
EVENTS_PER_PAGE = 4

@pytest.fixture()
def get_currency(db):
    return Currency.objects.create(
        code='USD',
        name='US Dollar',
        symbol='$',
    )


@pytest.fixture()
def create_events(db, get_currency):
    def index(owner: User = None, session_key: str = None) -> list[Event]:
        return [
            Event.objects.create(
                name=f"{owner.username if owner else session_key} event-{i+1}",
                currency=get_currency,
                session_id=session_key,
                owner=owner
            )
            for i in range(CREATED_EVENTS_COUNT)
        ]

    return index


@pytest.mark.django_db
class TestPrivateEventListView:
    def test_events_from_other_users_should_not_be_displayed(self, django_user_model, client, get_currency):
        log_user = django_user_model.objects.create(
            username='log-user',
            password='log-user-password'
        )

        user = django_user_model.objects.create(
            username='user',
            password='test-user-password'
        )

        client.force_login(log_user)

        url = reverse_lazy('service:event-list')

        Event.objects.create(
            name=f"Event from test-user",
            currency=get_currency,
            session_id=None,
            owner=user
        )

        Event.objects.create(
            name=f"Event from log-user",
            currency=get_currency,
            session_id=None,
            owner=log_user
        )

        response = client.get(url + '?page=1')

        assert "Event from log-user" in response.content.decode()
        assert "Event from test-user" not in response.content.decode()


    def test_events_should_be_displayed_for_authenticated_user(self, django_user_model, client, create_events):
        user = django_user_model.objects.create(
            username='test-user',
            password='test-user-password'
        )

        create_events(owner=user)

        client.force_login(user)

        url = reverse_lazy('service:event-list')

        response = client.get(url + '?page=1')


        assert response.status_code == 200
        assert response.context['page_obj'].number == 1
        assert len(response.context['object_list']) == EVENTS_PER_PAGE

        assert f"{user.username} event-10" in response.content.decode()
        assert f"{user.username} event-9" in response.content.decode()
        assert f"{user.username} event-8" in response.content.decode()
        assert f"{user.username} event-7" in response.content.decode()
        assert f"{user.username} event-6" not in response.content.decode()

        response = client.get(url + '?page=2')

        assert f"{user.username} event-6" in response.content.decode()
        assert f"{user.username} event-5" in response.content.decode()
        assert f"{user.username} event-4" in response.content.decode()
        assert f"{user.username} event-3" in response.content.decode()
        assert f"{user.username} event-2" not in response.content.decode()

        response = client.get(url + '?page=3')

        assert f"{user.username} event-2" in response.content.decode()
        assert f"{user.username} event-1" in response.content.decode()


@pytest.mark.django_db
class TestPublicEventListView:
    def test_events_should_be_displayed_for_anonym_user(self, django_user_model, client, create_events):
        session = client.session
        session.save()

        create_events(session_key=session.session_key)

        url = reverse_lazy('service:event-list')

        response = client.get(url + '?page=1')


        assert response.status_code == 200
        assert response.context['page_obj'].number == 1
        assert len(response.context['object_list']) == EVENTS_PER_PAGE

        assert f"{session.session_key} event-10" in response.content.decode()
        assert f"{session.session_key} event-9" in response.content.decode()
        assert f"{session.session_key} event-8" in response.content.decode()
        assert f"{session.session_key} event-7" in response.content.decode()
        assert f"{session.session_key} event-6" not in response.content.decode()

        response = client.get(url + '?page=2')

        assert f"{session.session_key} event-6" in response.content.decode()
        assert f"{session.session_key} event-5" in response.content.decode()
        assert f"{session.session_key} event-4" in response.content.decode()
        assert f"{session.session_key} event-3" in response.content.decode()
        assert f"{session.session_key} event-2" not in response.content.decode()

        response = client.get(url + '?page=3')

        assert f"{session.session_key} event-2" in response.content.decode()
        assert f"{session.session_key} event-1" in response.content.decode()