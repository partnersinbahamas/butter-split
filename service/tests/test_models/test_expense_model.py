import pytest
from decimal import Decimal
from typing import Callable

from django.core.exceptions import ValidationError

from service.models import Event, User, Participant, Expense, Currency

@pytest.fixture()
def get_currency(db):
    return Currency.objects.create(
        code='USD',
        name='US Dollar',
        symbol='$',
    )

@pytest.fixture()
def get_participant(db) -> Participant:
    return Participant.objects.create(
        name="test-participant",
    )

@pytest.fixture()
def get_event(db, get_currency, get_participant) -> Callable:
    def index(owner: User = None) -> Event:
        event = Event(name='test-event', owner=owner, currency=get_currency)
        event.save()
        event.participants.set([get_participant])

        return event

    return index

@pytest.fixture()
def get_expense(db, get_participant) -> Callable:
    def index(event: Event, payer: Participant = None) -> Expense:
        expense = Expense(name="test-expense", amount=Decimal("100.49"), event=event, payer=get_participant)

        if payer:
            expense.payer = payer

        return expense

    return index


@pytest.mark.django_db
class TestExpenseModel:
    def test_currency_string_representation(self, django_user_model, get_event, get_expense):
        user = django_user_model.objects.create_user(username='test-user', password='test-password')

        event = get_event(owner=user)
        expense = get_expense(event=event)
        expense.save()

        assert str(expense) == f"{expense.name} - {expense.payer.name}"

    def test_expense_should_be_created(self, django_user_model, get_event, get_expense, get_participant):
        user = django_user_model.objects.create_user(username='test-user', password='test-password')

        event = get_event(owner=user)
        expense = get_expense(event=event)
        expense.save()

        assert expense.name == 'test-expense'
        assert expense.amount == Decimal("100.49")
        assert expense.event == event
        assert expense.payer == get_participant

    def test_expense_payer_validation(self, django_user_model, get_event, get_expense, get_participant):
        user = django_user_model.objects.create_user(username='test-user', password='test-password')

        event = get_event(owner=user)
        payer = Participant.objects.create(name='expense-payer')
        expense = get_expense(event=event, payer=payer)

        with pytest.raises(ValidationError) as cleanInfo:
            expense.clean()

        assert f'{payer.name} participant is not part of the event {event.name}.' in str(cleanInfo.value)
