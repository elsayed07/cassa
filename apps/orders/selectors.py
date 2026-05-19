from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

from apps.orders.models import Order

if TYPE_CHECKING:
    from apps.accounts.models import User


class OrderSelector:
    @staticmethod
    def for_user(user: "User") -> QuerySet[Order]:
        return (
            Order.objects.filter(user=user)
            .prefetch_related("items", "events")
            .order_by("-created_at")
        )

    @staticmethod
    def by_number(number: str) -> Order:
        from shared.exceptions import NotFoundError

        try:
            return Order.objects.prefetch_related("items", "events", "refunds").get(number=number)
        except Order.DoesNotExist:
            raise NotFoundError(f"Order #{number} not found")
