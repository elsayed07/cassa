from __future__ import annotations

from apps.tax.models import TaxRate, TaxZone
from shared.money import Money


class TaxCalculator:
    @staticmethod
    def compute(subtotal: Money, country: str) -> Money:
        try:
            zone = TaxZone.objects.get(countries__contains=[country], is_active=True)
            rate = zone.rates.filter(is_active=True).first()
        except TaxZone.DoesNotExist:
            return Money.zero(subtotal.currency)

        if rate is None:
            return Money.zero(subtotal.currency)

        if rate.is_inclusive:
            tax = subtotal.amount * rate.rate / (1 + rate.rate)
        else:
            tax = subtotal.amount * rate.rate

        return Money(tax, subtotal.currency)
