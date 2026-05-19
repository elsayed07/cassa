from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models

from shared.models import BaseModel


class PaymentIntent(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payment_intents")
    provider = models.CharField(max_length=50, default="stripe")
    provider_intent_id = models.CharField(max_length=200, unique=True, db_index=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    class Meta(BaseModel.Meta):
        db_table = "payments_intent"

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_intent_id}"


class WebhookEvent(models.Model):
    """Deduplication record for incoming webhook events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, default="stripe")
    provider_event_id = models.CharField(max_length=200, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments_webhook_event"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_event_id} ({self.event_type})"
