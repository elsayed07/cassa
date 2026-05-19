from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from shared.exceptions import CouponError
from shared.money import Money


def _usd(amount: str) -> Money:
    return Money(Decimal(amount), "USD")


@pytest.mark.django_db
class TestCouponValidationOrder:
    def test_inactive_coupon_rejected(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(is_active=False)
        with pytest.raises(CouponError, match="expired or inactive"):
            CouponService.validate(coupon.code, None, _usd("100.00"))

    def test_expired_coupon_rejected(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(valid_to=timezone.now() - timedelta(hours=1))
        with pytest.raises(CouponError, match="expired or inactive"):
            CouponService.validate(coupon.code, None, _usd("100.00"))

    def test_min_subtotal_checked_before_max_uses(self) -> None:
        """When both min_subtotal and max_uses would fail, min_subtotal error is raised first."""
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(min_subtotal=Decimal("200.00"), max_uses=0)
        with pytest.raises(CouponError, match="Minimum order amount"):
            CouponService.validate(coupon.code, None, _usd("50.00"))

    def test_max_uses_exhausted_raises(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(max_uses=0, min_subtotal=Decimal("0"))
        with pytest.raises(CouponError, match="usage limit"):
            CouponService.validate(coupon.code, None, _usd("100.00"))

    def test_per_user_limit_not_triggered_without_prior_redemption(self) -> None:
        """A user with no prior redemptions should pass the per-user check."""
        from apps.coupons.services.coupon import CouponService
        from tests.factories.accounts import UserFactory
        from tests.factories.coupons import CouponFactory

        user = UserFactory()
        coupon = CouponFactory(max_uses_per_user=1)
        # No prior redemptions → should not raise
        result = CouponService.validate(coupon.code, user, _usd("100.00"))
        assert result == coupon

    def test_valid_coupon_returned(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory()
        result = CouponService.validate(coupon.code, None, _usd("100.00"))
        assert result == coupon

    def test_unknown_code_raises(self) -> None:
        from apps.coupons.services.coupon import CouponService

        with pytest.raises(CouponError, match="not found"):
            CouponService.validate("DOESNOTEXIST", None, _usd("100.00"))


@pytest.mark.django_db
class TestCouponDiscountComputation:
    def test_percentage_discount(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(discount_type="percentage", value=Decimal("10"))
        discount = CouponService.compute_discount(coupon, _usd("100.00"))
        assert discount.amount == Decimal("10.00")

    def test_percentage_discount_rounds(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(discount_type="percentage", value=Decimal("10"))
        discount = CouponService.compute_discount(coupon, _usd("33.00"))
        assert discount.currency == "USD"
        assert discount.amount == Decimal("3.30")

    def test_fixed_discount(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(discount_type="fixed", value=Decimal("15.00"))
        discount = CouponService.compute_discount(coupon, _usd("100.00"))
        assert discount.amount == Decimal("15.00")

    def test_fixed_discount_capped_at_subtotal(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(discount_type="fixed", value=Decimal("200.00"))
        discount = CouponService.compute_discount(coupon, _usd("50.00"))
        assert discount.amount == Decimal("50.00")

    def test_free_shipping_discount_is_zero(self) -> None:
        from apps.coupons.services.coupon import CouponService
        from tests.factories.coupons import CouponFactory

        coupon = CouponFactory(discount_type="free_shipping")
        discount = CouponService.compute_discount(coupon, _usd("100.00"))
        assert discount.amount == Decimal("0")
