import pytest
from decimal import Decimal

from shared.money import Money


def test_addition():
    assert Money("10.00", "USD") + Money("5.00", "USD") == Money("15.00", "USD")


def test_subtraction():
    assert Money("10.00", "USD") - Money("3.00", "USD") == Money("7.00", "USD")


def test_multiplication():
    assert Money("10.00", "USD") * 3 == Money("30.00", "USD")


def test_currency_mismatch_raises():
    with pytest.raises(ValueError, match="Cannot mix currencies"):
        Money("10.00", "USD") + Money("10.00", "EUR")


def test_zero():
    assert Money.zero("USD").is_zero()


def test_as_cents():
    assert Money("12.50", "USD").as_cents() == 1250


def test_from_cents():
    assert Money.from_cents(1250, "USD") == Money("12.50", "USD")


def test_jpy_zero_decimal():
    m = Money("1000", "JPY")
    assert m.amount == Decimal("1000")
    assert m.as_cents() == 1000
