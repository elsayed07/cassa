from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from shared.money import Money


@dataclass
class PriceBreakdown:
    currency: str
    subtotal: Money
    discount: Money = field(default_factory=lambda: Money(0, "USD"))
    tax: Money = field(default_factory=lambda: Money(0, "USD"))
    shipping: Money = field(default_factory=lambda: Money(0, "USD"))

    def __post_init__(self) -> None:
        zero = Money.zero(self.currency)
        if self.discount == Money(0, "USD"):
            self.discount = zero
        if self.tax == Money(0, "USD"):
            self.tax = zero
        if self.shipping == Money(0, "USD"):
            self.shipping = zero

    @property
    def grand_total(self) -> Money:
        return self.subtotal - self.discount + self.tax + self.shipping

    @property
    def discount_percentage(self) -> Decimal:
        if self.subtotal.is_zero():
            return Decimal("0")
        return (self.discount.amount / self.subtotal.amount * 100).quantize(Decimal("0.01"))
