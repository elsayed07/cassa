from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.core.cache import cache


def invalidate_keys(*keys: str) -> None:
    cache.delete_many(list(keys))


def get_or_set(key: str, fn: Callable[[], Any], timeout: int = 300) -> Any:
    value = cache.get(key)
    if value is None:
        value = fn()
        cache.set(key, value, timeout)
    return value


class CacheKey:
    """Central registry of cache key patterns to avoid typos and duplication."""

    @staticmethod
    def product_detail(product_id: str) -> str:
        return f"product:{product_id}:detail"

    @staticmethod
    def product_reviews(product_id: str) -> str:
        return f"product:{product_id}:reviews"

    @staticmethod
    def cart(cart_id: str) -> str:
        return f"cart:{cart_id}"

    @staticmethod
    def recommendations(product_id: str) -> str:
        return f"recommendations:{product_id}"

    @staticmethod
    def category_tree() -> str:
        return "catalog:category:tree"

    @staticmethod
    def review_aggregate(product_id: str) -> str:
        return f"product:{product_id}:review_aggregate"
