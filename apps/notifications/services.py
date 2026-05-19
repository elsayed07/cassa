from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from apps.carts.models import Cart
    from apps.orders.models import Order


class NotificationService:
    @staticmethod
    def send_order_confirmation(order: "Order") -> None:
        if not order.user or not order.user.email:
            return
        html = render_to_string("emails/order_confirmation.html", {"order": order})
        text = render_to_string("emails/order_confirmation.txt", {"order": order})
        msg = EmailMultiAlternatives(
            subject=f"Order Confirmed: #{order.number}",
            body=text,
            to=[order.user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

    @staticmethod
    def send_abandoned_cart(cart: "Cart") -> None:
        if not cart.user or not cart.user.email:
            return
        html = render_to_string("emails/abandoned_cart.html", {"cart": cart})
        text = render_to_string("emails/abandoned_cart.txt", {"cart": cart})
        msg = EmailMultiAlternatives(
            subject="You left something behind",
            body=text,
            to=[cart.user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

    @staticmethod
    def send_refund_notification(order: "Order", amount: str) -> None:
        if not order.user or not order.user.email:
            return
        html = render_to_string("emails/refund_issued.html", {"order": order, "amount": amount})
        msg = EmailMultiAlternatives(
            subject=f"Refund Processed for Order #{order.number}",
            body=f"Your refund of {amount} has been processed.",
            to=[order.user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
