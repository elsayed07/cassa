from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from shared.models import BaseModel


class Coupon(BaseModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"
        FREE_SHIPPING = "free_shipping", "Free Shipping"

    class AppliesTo(models.TextChoices):
        ALL = "all", "All Products"
        CATEGORY = "category", "Specific Categories"
        PRODUCT = "product", "Specific Products"

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=15, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    min_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    applies_to = models.CharField(max_length=10, choices=AppliesTo.choices, default=AppliesTo.ALL)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "coupons_coupon"

    def __str__(self) -> str:
        return self.code

    def is_valid(self) -> bool:
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="redemptions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    order = models.OneToOneField(
        "orders.Order", on_delete=models.PROTECT, related_name="coupon_redemption"
    )
    redeemed_at = models.DateTimeField(auto_now_add=True)
    discount_applied = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "coupons_redemption"
        indexes = [models.Index(fields=["coupon", "user"])]

    def __str__(self) -> str:
        return f"{self.coupon.code} → {self.user}"
