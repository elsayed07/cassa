from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Currencies that use 0 decimal places
ZERO_DECIMAL_CURRENCIES = {"JPY", "KRW", "CLP", "HUF", "TWD", "UGX", "VND"}


def _quantize(amount: Decimal, currency: str) -> Decimal:
    if currency.upper() in ZERO_DECIMAL_CURRENCIES:
        return amount.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


class Money:
    """Immutable value object pairing a Decimal amount with an ISO-4217 currency code."""

    __slots__ = ("_amount", "_currency")

    def __init__(self, amount: Decimal | int | str | float, currency: str) -> None:
        self._currency = currency.upper()
        self._amount = _quantize(Decimal(str(amount)), self._currency)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    def _check_currency(self, other: "Money") -> None:
        if self._currency != other._currency:
            raise ValueError(
                f"Cannot mix currencies: {self._currency} and {other._currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, factor: Decimal | int | float) -> "Money":
        return Money(self._amount * Decimal(str(factor)), self._currency)

    def __rmul__(self, factor: Decimal | int | float) -> "Money":
        return self.__mul__(factor)

    def __truediv__(self, divisor: Decimal | int | float) -> "Money":
        return Money(self._amount / Decimal(str(divisor)), self._currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount == other._amount and self._currency == other._currency

    def __lt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount <= other._amount

    def __gt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount >= other._amount

    def __repr__(self) -> str:
        return f"Money({self._amount!r}, {self._currency!r})"

    def __str__(self) -> str:
        return f"{self._currency} {self._amount}"

    def __hash__(self) -> int:
        return hash((self._amount, self._currency))

    def is_zero(self) -> bool:
        return self._amount == Decimal("0")

    def as_cents(self) -> int:
        """Return integer cents (or smallest unit). Used for Stripe amounts."""
        if self._currency.upper() in ZERO_DECIMAL_CURRENCIES:
            return int(self._amount)
        return int(self._amount * 100)

    @classmethod
    def zero(cls, currency: str) -> "Money":
        return cls(Decimal("0"), currency)

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> "Money":
        if currency.upper() in ZERO_DECIMAL_CURRENCIES:
            return cls(Decimal(cents), currency)
        return cls(Decimal(cents) / 100, currency)
