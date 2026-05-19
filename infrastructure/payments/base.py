from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from shared.money import Money

if TYPE_CHECKING:
    from apps.orders.models import Order


@dataclass(frozen=True)
class IntentResult:
    provider_intent_id: str
    client_secret: str
    status: str
    amount: Money


@dataclass(frozen=True)
class RefundResult:
    provider_refund_id: str
    status: str
    amount: Money


class PaymentProvider(Protocol):
    """Protocol that every payment adapter must satisfy."""

    def create_intent(self, order: "Order") -> IntentResult: ...

    def retrieve_intent(self, provider_intent_id: str) -> IntentResult: ...

    def refund(self, provider_intent_id: str, amount: Money | None = None) -> RefundResult: ...

    def verify_webhook(self, payload: bytes, signature: str) -> dict: ...
