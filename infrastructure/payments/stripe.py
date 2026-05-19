from __future__ import annotations

from typing import TYPE_CHECKING

import stripe
from django.conf import settings

from infrastructure.payments.base import IntentResult, RefundResult
from shared.exceptions import PaymentError
from shared.money import Money

if TYPE_CHECKING:
    from apps.orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeProvider:
    """Stripe PaymentIntent adapter."""

    def create_intent(self, order: "Order") -> IntentResult:
        try:
            intent = stripe.PaymentIntent.create(
                amount=order.grand_total.as_cents(),
                currency=order.currency.lower(),
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.number,
                },
                idempotency_key=f"order-{order.id}",
            )
        except stripe.StripeError as exc:
            raise PaymentError(str(exc)) from exc

        return IntentResult(
            provider_intent_id=intent.id,
            client_secret=intent.client_secret,
            status=intent.status,
            amount=Money.from_cents(intent.amount, order.currency),
        )

    def retrieve_intent(self, provider_intent_id: str) -> IntentResult:
        try:
            intent = stripe.PaymentIntent.retrieve(provider_intent_id)
        except stripe.StripeError as exc:
            raise PaymentError(str(exc)) from exc

        return IntentResult(
            provider_intent_id=intent.id,
            client_secret=intent.client_secret or "",
            status=intent.status,
            amount=Money.from_cents(intent.amount, intent.currency.upper()),
        )

    def refund(self, provider_intent_id: str, amount: Money | None = None) -> RefundResult:
        try:
            intent = stripe.PaymentIntent.retrieve(provider_intent_id)
            kwargs: dict = {"payment_intent": provider_intent_id}
            if amount is not None:
                kwargs["amount"] = amount.as_cents()
            refund = stripe.Refund.create(**kwargs)
        except stripe.StripeError as exc:
            raise PaymentError(str(exc)) from exc

        refund_currency = intent.currency.upper()
        refund_amount = amount or Money.from_cents(refund.amount, refund_currency)
        return RefundResult(
            provider_refund_id=refund.id,
            status=refund.status,
            amount=refund_amount,
        )

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (stripe.SignatureVerificationError, ValueError) as exc:
            raise PaymentError(f"Invalid webhook signature: {exc}") from exc
        return dict(event)
