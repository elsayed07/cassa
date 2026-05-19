from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.payments.models import WebhookEvent
from infrastructure.payments.stripe import StripeProvider
from shared.exceptions import PaymentError


@require_POST
@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    provider = StripeProvider()
    try:
        event = provider.verify_webhook(payload, signature)
    except PaymentError:
        return HttpResponse(status=400)

    event_id = event.get("id", "")
    event_type = event.get("type", "")

    webhook_event, created = WebhookEvent.objects.get_or_create(
        provider_event_id=event_id,
        defaults={
            "provider": "stripe",
            "event_type": event_type,
            "payload": event,
        },
    )

    if not created:
        return HttpResponse(status=200)

    from django.db import transaction

    transaction.on_commit(
        lambda: _process_event.delay(str(webhook_event.id))
    )

    return HttpResponse(status=200)


from celery import shared_task


@shared_task(name="payments.process_stripe_event", bind=True, max_retries=5)
def _process_event(self, webhook_event_id: str) -> None:  # type: ignore[misc]
    try:
        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        if webhook_event.processed:
            return
        _dispatch_event(webhook_event)
        webhook_event.processed = True
        webhook_event.save(update_fields=["processed"])
    except Exception as exc:
        WebhookEvent.objects.filter(id=webhook_event_id).update(error=str(exc))
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 10)


def _dispatch_event(webhook_event: WebhookEvent) -> None:
    from apps.orders.models import Order
    from apps.orders.services.checkout import CheckoutService
    from apps.payments.models import PaymentIntent

    event = webhook_event.payload
    event_type = webhook_event.event_type

    if event_type in ("payment_intent.succeeded",):
        intent_id = event["data"]["object"]["id"]
        try:
            payment_intent = PaymentIntent.objects.select_related("order").get(
                provider_intent_id=intent_id
            )
        except PaymentIntent.DoesNotExist:
            return
        order = payment_intent.order
        if order.status == Order.Status.AWAITING_PAYMENT:
            CheckoutService.confirm_payment(order)

    elif event_type in ("payment_intent.payment_failed", "checkout.session.expired"):
        obj = event["data"]["object"]
        intent_id = obj.get("id") or obj.get("payment_intent", "")
        try:
            payment_intent = PaymentIntent.objects.select_related("order").get(
                provider_intent_id=intent_id
            )
            order = payment_intent.order
            if order.status == Order.Status.AWAITING_PAYMENT:
                CheckoutService.cancel_order(order)
        except PaymentIntent.DoesNotExist:
            pass

    elif event_type == "charge.refunded":
        charge = event["data"]["object"]
        intent_id = charge.get("payment_intent", "")
        refund_obj = charge.get("refunds", {}).get("data", [{}])[0]
        if refund_obj:
            from apps.orders.models import Order, OrderEvent, Refund
            from shared.money import Money
            try:
                payment_intent = PaymentIntent.objects.select_related("order").get(
                    provider_intent_id=intent_id
                )
                order = payment_intent.order
                refund_amount = Money.from_cents(refund_obj.get("amount", 0), charge.get("currency", "usd").upper())
                Refund.objects.get_or_create(
                    provider_refund_id=refund_obj["id"],
                    defaults={
                        "order": order,
                        "amount": refund_amount.amount,
                        "status": refund_obj.get("status", "succeeded"),
                    },
                )
                if order.status == Order.Status.PAID:
                    order.mark_refunded()
                    OrderEvent.objects.create(order=order, status=Order.Status.REFUNDED)
            except PaymentIntent.DoesNotExist:
                pass
