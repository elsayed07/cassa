from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from shared.models import BaseModel
from shared.state_machine import transition


class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting Payment"
        PAID = "paid", "Paid"
        FULFILLED = "fulfilled", "Fulfilled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"
        REFUND_FAILED = "refund_failed", "Refund Failed"

    number = models.CharField(max_length=20, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    currency = models.CharField(max_length=3, default="USD")

    # Snapshotted addresses at time of order
    shipping_address = models.JSONField()
    billing_address = models.JSONField()

    # Snapshotted financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    # Coupon snapshot
    coupon_code = models.CharField(max_length=50, blank=True)
    coupon_discount_type = models.CharField(max_length=15, blank=True)

    # Shipping method snapshot
    shipping_method_name = models.CharField(max_length=200, blank=True)

    # Stock reservation tracking
    reservation_uuid = models.UUIDField(null=True, blank=True)

    # Shipping tracking
    tracking_number = models.CharField(max_length=200, blank=True)
    tracking_url = models.URLField(blank=True)

    class Meta(BaseModel.Meta):
        db_table = "orders_order"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Order #{self.number}"

    @property
    def grand_total_money(self):  # type: ignore[return]
        from shared.money import Money
        return Money(self.grand_total, self.currency)

    @transition(field="status", source=Status.PENDING, target=Status.AWAITING_PAYMENT)
    def mark_awaiting_payment(self) -> None:
        pass

    @transition(field="status", source=Status.AWAITING_PAYMENT, target=Status.PAID)
    def mark_paid(self) -> None:
        pass

    @transition(field="status", source=Status.PAID, target=Status.FULFILLED)
    def mark_fulfilled(self) -> None:
        pass

    @transition(field="status", source=Status.FULFILLED, target=Status.COMPLETED)
    def mark_completed(self) -> None:
        pass

    @transition(
        field="status",
        source=[Status.PENDING, Status.AWAITING_PAYMENT, Status.PAID],
        target=Status.CANCELLED,
    )
    def cancel(self) -> None:
        pass

    @transition(field="status", source=Status.PAID, target=Status.REFUNDED)
    def mark_refunded(self) -> None:
        pass

    @transition(field="status", source=Status.PAID, target=Status.REFUND_FAILED)
    def mark_refund_failed(self) -> None:
        pass


class OrderItem(models.Model):
    """Immutable snapshot of a product variant at order time. Never modify after creation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant_id = models.UUIDField()
    product_name = models.CharField(max_length=400)
    variant_name = models.CharField(max_length=200, blank=True)
    sku = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "orders_order_item"

    def __str__(self) -> str:
        return f"{self.quantity}× {self.sku} ({self.order})"


class OrderEvent(models.Model):
    """Immutable audit trail of status transitions and notes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_order_event"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.order} → {self.status}"


class Refund(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_refund_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta(BaseModel.Meta):
        db_table = "orders_refund"

    def __str__(self) -> str:
        return f"Refund {self.provider_refund_id} for {self.order}"
