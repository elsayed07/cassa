from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from apps.coupons.models import Coupon
from shared.exceptions import CouponError
from shared.money import Money

if TYPE_CHECKING:
    from apps.accounts.models import User


class CouponService:
    @staticmethod
    def validate(code: str, user: "User | None", subtotal: Money) -> Coupon:
        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            raise CouponError("Coupon code not found.")

        if not coupon.is_valid():
            raise CouponError("This coupon is expired or inactive.")

        if subtotal.amount < coupon.min_subtotal:
            raise CouponError(
                f"Minimum order amount for this coupon is {coupon.min_subtotal}."
            )

        if coupon.max_uses is not None and coupon.redemptions.count() >= coupon.max_uses:
            raise CouponError("This coupon has reached its usage limit.")

        if user and coupon.max_uses_per_user:
            if coupon.redemptions.filter(user=user).count() >= coupon.max_uses_per_user:
                raise CouponError("You have already used this coupon the maximum number of times.")

        return coupon

    @staticmethod
    def compute_discount(coupon: Coupon, subtotal: Money) -> Money:
        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            discount = subtotal.amount * (coupon.value / Decimal("100"))
            return Money(discount, subtotal.currency)
        elif coupon.discount_type == Coupon.DiscountType.FIXED:
            fixed = min(coupon.value, subtotal.amount)
            return Money(fixed, subtotal.currency)
        else:
            return Money.zero(subtotal.currency)
