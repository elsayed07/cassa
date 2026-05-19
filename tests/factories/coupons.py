import factory
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.coupons.models import Coupon


class CouponFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: f"COUPON{n:04d}")
    discount_type = Coupon.DiscountType.PERCENTAGE
    value = Decimal("10")
    valid_from = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    valid_to = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    max_uses = None
    max_uses_per_user = 1
    min_subtotal = Decimal("0")
    is_active = True

    class Meta:
        model = Coupon
