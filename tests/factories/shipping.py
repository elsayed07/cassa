import factory
from decimal import Decimal

from apps.shipping.models import ShippingMethod, ShippingZone


class ShippingZoneFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Zone {n}")
    countries = ["US"]
    is_active = True

    class Meta:
        model = ShippingZone


class ShippingMethodFactory(factory.django.DjangoModelFactory):
    zone = factory.SubFactory(ShippingZoneFactory)
    name = factory.Sequence(lambda n: f"Standard Shipping {n}")
    rate_type = ShippingMethod.RateType.FLAT
    base_rate = Decimal("5.00")
    is_active = True

    class Meta:
        model = ShippingMethod
