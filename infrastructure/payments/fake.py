from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from infrastructure.payments.base import IntentResult, RefundResult
from shared.money import Money

if TYPE_CHECKING:
    from apps.orders.models import Order


class FakePaymentProvider:
    """In-memory payment provider for tests. Never hits external APIs."""

    def create_intent(self, order: "Order") -> IntentResult:
        return IntentResult(
            provider_intent_id=f"pi_fake_{uuid.uuid4().hex[:12]}",
            client_secret="fake_client_secret",
            status="requires_payment_method",
            amount=order.grand_total,
        )

    def retrieve_intent(self, provider_intent_id: str) -> IntentResult:
        return IntentResult(
            provider_intent_id=provider_intent_id,
            client_secret="fake_client_secret",
            status="succeeded",
            amount=Money(100, "USD"),
        )

    def refund(self, provider_intent_id: str, amount: Money | None = None) -> RefundResult:
        return RefundResult(
            provider_refund_id=f"re_fake_{uuid.uuid4().hex[:12]}",
            status="succeeded",
            amount=amount or Money(100, "USD"),
        )

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        import json

        return json.loads(payload)
