from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalog.models.product import ProductVariant
from shared.models import BaseModel


class Cart(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True, db_index=True)
    coupon = models.ForeignKey(
        "coupons.Coupon", on_delete=models.SET_NULL, null=True, blank=True
    )
    recovery_email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "carts_cart"

    def __str__(self) -> str:
        return f"Cart({self.user or self.session_key})"

    @property
    def subtotal(self) -> Decimal:
        return sum(item.line_total for item in self.items.all()) or Decimal("0")

    @property
    def item_count(self) -> int:
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    @property
    def currency(self) -> str:
        first = self.items.select_related("variant__product").first()
        return first.variant.product.currency if first else settings.CASSA_CURRENCY


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "carts_cart_item"
        unique_together = [["cart", "variant"]]

    def __str__(self) -> str:
        return f"{self.quantity}× {self.variant.sku}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
