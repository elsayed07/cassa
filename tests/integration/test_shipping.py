from __future__ import annotations

from decimal import Decimal

import pytest

from shared.money import Money


@pytest.mark.django_db
class TestShippingCalculator:
    def test_returns_empty_for_unknown_country(self) -> None:
        from apps.shipping.services.calculator import ShippingCalculator
        from tests.factories.carts import CartFactory, CartItemFactory
        from tests.factories.shipping import ShippingZoneFactory

        ShippingZoneFactory(countries=["GB"])
        cart = CartFactory()
        CartItemFactory(cart=cart)

        results = ShippingCalculator.options_for(cart, "DE")
        assert results == []

    def test_returns_methods_for_matching_country(self) -> None:
        from apps.shipping.models import ShippingMethod
        from apps.shipping.services.calculator import ShippingCalculator
        from tests.factories.carts import CartFactory, CartItemFactory
        from tests.factories.shipping import ShippingMethodFactory, ShippingZoneFactory

        zone = ShippingZoneFactory(countries=["US"])
        ShippingMethodFactory(zone=zone, base_rate=Decimal("5.00"), rate_type=ShippingMethod.RateType.FLAT)

        cart = CartFactory()
        CartItemFactory(cart=cart)

        results = ShippingCalculator.options_for(cart, "US")
        assert len(results) == 1
        method, cost = results[0]
        assert isinstance(cost, Money)
        assert cost.amount == Decimal("5.00")

    def test_free_shipping_method_costs_zero(self) -> None:
        from apps.shipping.models import ShippingMethod
        from apps.shipping.services.calculator import ShippingCalculator
        from tests.factories.carts import CartFactory, CartItemFactory
        from tests.factories.shipping import ShippingMethodFactory, ShippingZoneFactory

        zone = ShippingZoneFactory(countries=["US"])
        ShippingMethodFactory(zone=zone, rate_type=ShippingMethod.RateType.FREE)

        cart = CartFactory()
        CartItemFactory(cart=cart)

        results = ShippingCalculator.options_for(cart, "US")
        assert len(results) == 1
        _, cost = results[0]
        assert cost.amount == Decimal("0")

    def test_inactive_zone_not_returned(self) -> None:
        from apps.shipping.services.calculator import ShippingCalculator
        from tests.factories.carts import CartFactory, CartItemFactory
        from tests.factories.shipping import ShippingMethodFactory, ShippingZoneFactory

        zone = ShippingZoneFactory(countries=["US"], is_active=False)
        ShippingMethodFactory(zone=zone)

        cart = CartFactory()
        CartItemFactory(cart=cart)

        results = ShippingCalculator.options_for(cart, "US")
        assert results == []

    def test_empty_cart_returns_usd_default(self) -> None:
        from apps.shipping.services.calculator import ShippingCalculator
        from tests.factories.carts import CartFactory
        from tests.factories.shipping import ShippingMethodFactory, ShippingZoneFactory

        zone = ShippingZoneFactory(countries=["US"])
        ShippingMethodFactory(zone=zone, base_rate=Decimal("5.00"))

        cart = CartFactory()
        results = ShippingCalculator.options_for(cart, "US")
        assert len(results) == 1
        _, cost = results[0]
        assert cost.currency == "USD"
