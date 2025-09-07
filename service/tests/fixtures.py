import pytest

from service.models import Currency, Participant

@pytest.fixture()
def get_currency(db):
    return Currency.objects.create(
        code='USD',
        name='US Dollar',
        symbol='$',
    )

@pytest.fixture()
def get_participant(db, get_user = None):
    return Participant.objects.create(
        name="test-participant",
        creator=get_user
    )
