from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Avg, Count, QuerySet

from apps.reviews.models import Review

if TYPE_CHECKING:
    from apps.catalog.models.product import Product


class ReviewSelector:
    @staticmethod
    def approved_for_product(product: "Product") -> QuerySet[Review]:
        return (
            Review.objects.filter(product=product, status=Review.Status.APPROVED)
            .select_related("user")
            .order_by("-created_at")
        )

    @staticmethod
    def aggregate(product: "Product") -> dict:
        from django.core.cache import cache
        from shared.cache import CacheKey

        key = CacheKey.review_aggregate(str(product.id))
        result = cache.get(key)
        if result is None:
            agg = Review.objects.filter(
                product=product, status=Review.Status.APPROVED
            ).aggregate(avg=Avg("rating"), count=Count("id"))
            result = {
                "avg": round(float(agg["avg"] or 0), 1),
                "count": agg["count"] or 0,
            }
            cache.set(key, result, timeout=300)
        return result
