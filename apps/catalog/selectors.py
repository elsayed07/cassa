from __future__ import annotations

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import QuerySet

from apps.catalog.models import Category, Product, ProductVariant


class ProductSelector:
    @staticmethod
    def active() -> QuerySet[Product]:
        return (
            Product.objects.filter(status=Product.Status.ACTIVE, deleted_at__isnull=True)
            .select_related("brand")
            .prefetch_related("variants", "images")
        )

    @staticmethod
    def by_category(category: Category) -> QuerySet[Product]:
        descendant_ids = [c.pk for c in category.get_descendants(include_self=True)]
        return ProductSelector.active().filter(category_id__in=descendant_ids)

    @staticmethod
    def featured() -> QuerySet[Product]:
        return ProductSelector.active().filter(is_featured=True)

    @staticmethod
    def search(query: str) -> QuerySet[Product]:
        search_query = SearchQuery(query, config="english")
        return (
            ProductSelector.active()
            .filter(search_vector=search_query)
            .annotate(rank=SearchRank("search_vector", search_query))
            .order_by("-rank")
        )

    @staticmethod
    def by_slug(slug: str) -> Product:
        from shared.exceptions import NotFoundError

        try:
            return (
                ProductSelector.active()
                .prefetch_related("variants__images", "images")
                .get(slug=slug)
            )
        except Product.DoesNotExist:
            raise NotFoundError(f"Product '{slug}' not found")


class CategorySelector:
    @staticmethod
    def active_roots() -> QuerySet[Category]:
        return Category.get_root_nodes().filter(is_active=True)

    @staticmethod
    def by_slug(slug: str) -> Category:
        from shared.exceptions import NotFoundError

        try:
            return Category.objects.get(slug=slug, is_active=True)
        except Category.DoesNotExist:
            raise NotFoundError(f"Category '{slug}' not found")
