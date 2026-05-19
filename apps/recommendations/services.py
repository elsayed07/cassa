from __future__ import annotations

from django.core.cache import cache


class RecommendationService:
    REDIS_KEY = "recommendations:{product_id}"
    MAX_RESULTS = 6

    @classmethod
    def for_product(cls, product_id: str, n: int = 6) -> list:
        from apps.catalog.models import Product

        key = cls.REDIS_KEY.format(product_id=product_id)
        raw_cache = cache.get(key)

        raw_client = cache.client.get_client()  # type: ignore[attr-defined]
        redis_key = f"co_purchase:{product_id}"
        top_ids = raw_client.zrevrange(redis_key, 0, n - 1)
        top_ids_str = [pid.decode() if isinstance(pid, bytes) else pid for pid in top_ids]

        if not top_ids_str:
            return []

        products = list(
            Product.objects.filter(
                id__in=top_ids_str, status=Product.Status.ACTIVE
            ).prefetch_related("images")[:n]
        )
        return sorted(products, key=lambda p: top_ids_str.index(str(p.id)))

    @classmethod
    def record_purchase(cls, product_ids: list[str]) -> None:
        if len(product_ids) < 2:
            return

        raw_client = cache.client.get_client()  # type: ignore[attr-defined]
        for i, pid in enumerate(product_ids):
            for j, other_pid in enumerate(product_ids):
                if i != j:
                    raw_client.zincrby(f"co_purchase:{pid}", 1, other_pid)
