from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from apps.shipping.models import ShippingMethod, ShippingZone
from shared.money import Money

if TYPE_CHECKING:
    from apps.carts.models import Cart


class ShippingCalculator:
    @staticmethod
    def options_for(cart: "Cart", country: str) -> list[tuple[ShippingMethod, Money]]:
        """Return available shipping methods and their costs for a country."""
        try:
            zone = ShippingZone.objects.get(
                countries__contains=[country], is_active=True
            )
        except ShippingZone.DoesNotExist:
            return []

        total_weight = Decimal("0")
        for item in cart.items.select_related("variant__product"):
            weight = item.variant.product.weight or Decimal("0")
            total_weight += weight * item.quantity

        methods = zone.methods.filter(is_active=True)
        currency = cart.items.first().variant.product.currency if cart.items.exists() else "USD"

        return [
            (method, Money(method.calculate_rate(total_weight), currency))
            for method in methods
        ]
