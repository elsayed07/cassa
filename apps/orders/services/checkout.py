from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string

from apps.inventory.services.stock import StockService
from apps.orders.models import Order, OrderEvent, OrderItem
from infrastructure.payments.base import IntentResult
from shared.exceptions import CartError
from shared.money import Money

if TYPE_CHECKING:
    from apps.accounts.models import Address, User
    from apps.carts.models import Cart
    from apps.shipping.models import ShippingMethod


def _generate_order_number() -> str:
    prefix = get_random_string(4, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    suffix = get_random_string(6, "0123456789")
    return f"{prefix}-{suffix}"


class CheckoutService:
    @staticmethod
    @transaction.atomic
    def create_order(
        cart: "Cart",
        shipping_address: "Address",
        billing_address: "Address",
        shipping_method: "ShippingMethod",
        user: "User | None" = None,
    ) -> tuple[Order, IntentResult]:
        from apps.coupons.services.coupon import CouponService
        from apps.tax.services.calculator import TaxCalculator
        from infrastructure.payments.stripe import StripeProvider

        if not cart.items.exists():
            raise CartError("Cart is empty.")

        cart_items = list(
            cart.items.select_related("variant__product", "variant__stock").all()
        )
        currency = cart.currency

        # Reserve stock for all items (raises StockError if any are unavailable)
        reservation_uuid = uuid.uuid4()
        for item in cart_items:
            StockService.reserve(str(item.variant_id), item.quantity, reservation_uuid)

        # Compute financials
        subtotal = Money(
            sum(item.line_total for item in cart_items), currency
        )
        country = shipping_address.country
        tax = TaxCalculator.compute(subtotal, country)
        shipping_cost = Money(shipping_method.calculate_rate(), currency)

        discount = Money.zero(currency)
        coupon_code = ""
        coupon_discount_type = ""
        if cart.coupon:
            discount = CouponService.compute_discount(cart.coupon, subtotal)
            coupon_code = cart.coupon.code
            coupon_discount_type = cart.coupon.discount_type

        grand_total = subtotal - discount + tax + shipping_cost

        order = Order.objects.create(
            number=_generate_order_number(),
            user=user,
            status=Order.Status.AWAITING_PAYMENT,
            currency=currency,
            shipping_address=shipping_address.as_dict(),
            billing_address=billing_address.as_dict(),
            subtotal=subtotal.amount,
            discount=discount.amount,
            tax=tax.amount,
            shipping_cost=shipping_cost.amount,
            grand_total=grand_total.amount,
            coupon_code=coupon_code,
            coupon_discount_type=coupon_discount_type,
            shipping_method_name=shipping_method.name,
            reservation_uuid=reservation_uuid,
        )

        # Snapshot line items
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                variant_id=item.variant_id,
                product_name=item.variant.product.safe_translation_getter("name", any_language=True) or "",
                variant_name=item.variant.name,
                sku=item.variant.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
            )
            for item in cart_items
        ])

        OrderEvent.objects.create(order=order, status=Order.Status.AWAITING_PAYMENT)

        # Create payment intent
        provider = StripeProvider()
        intent = provider.create_intent(order)

        from apps.payments.models import PaymentIntent as PaymentIntentModel
        PaymentIntentModel.objects.create(
            order=order,
            provider="stripe",
            provider_intent_id=intent.provider_intent_id,
            status=intent.status,
            amount=order.grand_total,
        )

        return order, intent

    @staticmethod
    @transaction.atomic
    def confirm_payment(order: Order) -> None:
        """Called by webhook handler after payment confirmation."""
        from apps.notifications.services import NotificationService
        from apps.recommendations.tasks import update_recommendation_scores

        order.mark_paid()
        OrderEvent.objects.create(order=order, status=Order.Status.PAID)

        # Commit the stock reservation
        if order.reservation_uuid:
            StockService.commit(order.reservation_uuid)

        # Record coupon redemption
        if order.coupon_code and order.user:
            from apps.coupons.models import Coupon, CouponRedemption
            try:
                coupon = Coupon.objects.get(code=order.coupon_code)
                CouponRedemption.objects.get_or_create(
                    coupon=coupon,
                    order=order,
                    defaults={"user": order.user, "discount_applied": order.discount},
                )
            except Coupon.DoesNotExist:
                pass

        # Async side effects on commit
        from django.db import transaction as db_transaction
        db_transaction.on_commit(lambda: _post_payment_tasks(order.id))

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order) -> None:
        order.cancel()
        if order.reservation_uuid:
            StockService.release(order.reservation_uuid)
        OrderEvent.objects.create(order=order, status=Order.Status.CANCELLED)


def _post_payment_tasks(order_id: uuid.UUID) -> None:
    from apps.notifications.tasks import send_order_confirmation
    from apps.orders.tasks import generate_invoice_pdf
    from apps.recommendations.tasks import update_recommendation_scores

    send_order_confirmation.delay(str(order_id))
    generate_invoice_pdf.delay(str(order_id))
    update_recommendation_scores.delay(str(order_id))
