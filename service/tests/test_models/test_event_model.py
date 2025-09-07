import pytest
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from service.models import Participant, User, Event, Currency
from service.tests.fixtures import get_currency, get_participant


@pytest.fixture()
def get_user(db):
    return get_user_model().objects.create_user(
        username="some-user",
        first_name="some-first-name",
        last_name="some-last-name",
        password="user-password"
    )

@pytest.mark.parametrize('event_name', ['test-event'])
@pytest.mark.django_db
class TestEventMode:
    def test_event_string_representation(
        self,
        event_name: str,
        get_currency: Currency,
        get_user: User
    ):
        event = Event.objects.create(
            name=event_name,
            owner=get_user,
            currency=get_currency,
        )

        assert str(event) == event_name

    def test_event_should_be_created_with_user(
        self,
        event_name: str,
        get_currency: Currency,
        get_user: User
    ):

        event = Event.objects.create(
            name=event_name,
            owner=get_user,
            currency=get_currency,
        )
        assert event.owner == get_user
        assert event.session_id is None

    def test_event_should_be_created_with_session_id(
        self,
        client,
        event_name: str,
        get_currency: Currency,
    ):

        session = client.session
        session.save()

        event = Event.objects.create(
            name=event_name,
            currency=get_currency,
            session_id=session.session_key
        )

        assert event.owner is None
        assert event.session_id == session.session_key


    def test_event_should_be_created(
        self,
        event_name: str,
        get_currency: Currency,
        get_participant: Participant,
        get_user: User
    ):

        event = Event.objects.create(
            name=event_name,
            owner=get_user,
            currency=get_currency,
        )

        event.participants.set([get_participant])

        assert event.currency == get_currency
        assert event.participants.count() == 1
        assert get_participant in event.participants.all()

    def test_event_name_and_owner_should_be_unique(
            self,
            event_name: str,
            get_currency: Currency,
            get_user: User
    ):
        # event-1
        Event.objects.create(
            name=event_name,
            owner=get_user,
            currency=get_currency,
        )

        with transaction.atomic():
            with pytest.raises(IntegrityError):
                # event-2
                Event.objects.create(
                    name=event_name,
                    owner=get_user,
                    currency=get_currency,
                )

        assert Event.objects.count() == 1
