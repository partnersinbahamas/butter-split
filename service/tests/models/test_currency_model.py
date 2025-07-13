import pytest
from django.db import IntegrityError, transaction

from service.models import Currency


@pytest.fixture(
    params=[
        (
            'USD',
            'US Dollar',
            '$',
        ),
    ],
    ids=['us-dollar-currency'],
)
def currency_data(request):
    return request.param


@pytest.mark.django_db
class TestCurrencyModel:
    def test_currency_string_representation(self, currency_data: tuple):
        code, name, symbol = currency_data

        currency = Currency.objects.create(code=code, name=name, symbol=symbol)
        assert str(currency) ==  f"{symbol} - {code}"

    def test_currency_should_be_unique(self, currency_data: tuple):
        code, name, symbol = currency_data

        # currency-1
        Currency.objects.create(code=code, name=name, symbol=symbol)

        with transaction.atomic():
            with pytest.raises(IntegrityError):
                #  currency-2
                Currency.objects.create(code=code, name=name, symbol=symbol)

        assert Currency.objects.count() == 1

    def test_currency_should_be_created(self, currency_data: tuple):
        code, name, symbol = currency_data

        currency = Currency.objects.create(code=code, name=name, symbol=symbol)

        assert currency.code == code
        assert currency.name == name
        assert currency.symbol == symbol