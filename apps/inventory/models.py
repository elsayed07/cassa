from __future__ import annotations

import uuid

from django.db import models

from apps.catalog.models.product import ProductVariant
from shared.models import BaseModel


class StockItem(BaseModel):
    """Current stock level for a variant at a location."""

    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name="stock")
    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    class Meta(BaseModel.Meta):
        db_table = "inventory_stock_item"

    def __str__(self) -> str:
        return f"Stock({self.variant.sku}): {self.available}"

    @property
    def available(self) -> int:
        return max(0, self.quantity_on_hand - self.quantity_reserved)

    @property
    def is_low(self) -> bool:
        return self.available <= self.low_stock_threshold


class StockMovement(models.Model):
    """Immutable audit log of every stock change."""

    class Type(models.TextChoices):
        RECEIVE = "receive", "Receive"
        RESERVE = "reserve", "Reserve"
        RELEASE = "release", "Release"
        SALE = "sale", "Sale"
        RETURN = "return", "Return"
        ADJUSTMENT = "adjustment", "Adjustment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name="movements")
    type = models.CharField(max_length=20, choices=Type.choices)
    quantity = models.IntegerField()
    reservation_uuid = models.UUIDField(null=True, blank=True, db_index=True)
    note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "inventory_stock_movement"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.type} {self.quantity} for {self.stock_item}"
