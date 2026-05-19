from django.conf import settings
from django.db import models

from shared.models.base import BaseModel


class EventType(models.TextChoices):
    PAGE_VIEW = "page_view", "Page View"
    PRODUCT_VIEW = "product_view", "Product View"
    ADD_TO_CART = "add_to_cart", "Add to Cart"
    REMOVE_FROM_CART = "remove_from_cart", "Remove from Cart"
    CHECKOUT_START = "checkout_start", "Checkout Start"
    PURCHASE = "purchase", "Purchase"
    SEARCH = "search", "Search"
    COUPON_APPLIED = "coupon_applied", "Coupon Applied"


class AnalyticsEvent(BaseModel):
    """Immutable append-only event record. Never updated after creation."""

    event_type = models.CharField(max_length=50, choices=EventType.choices, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    path = models.CharField(max_length=500, blank=True)
    # Flexible payload: product_id, query, coupon_code, order_id, etc.
    data = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.created_at:%Y-%m-%d %H:%M}"
