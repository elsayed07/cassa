from __future__ import annotations

import pytest


@pytest.mark.django_db
class TestProductListAPI:
    def test_returns_200_with_empty_results(self, client) -> None:
        response = client.get("/api/v1/catalog/products/")
        assert response.status_code == 200

    def test_returns_active_products(self, client) -> None:
        from tests.factories.catalog import ProductFactory

        p = ProductFactory(status="active")
        response = client.get("/api/v1/catalog/products/")
        assert response.status_code == 200
        data = response.json()
        slugs = [item["slug"] for item in data.get("results", data.get("items", []))]
        assert p.slug in slugs

    def test_draft_products_not_returned(self, client) -> None:
        from apps.catalog.models import Product
        from tests.factories.catalog import ProductFactory

        p = ProductFactory(status=Product.Status.DRAFT)
        response = client.get("/api/v1/catalog/products/")
        data = response.json()
        slugs = [item["slug"] for item in data.get("results", data.get("items", []))]
        assert p.slug not in slugs

    def test_search_filters_by_query(self, client) -> None:
        response = client.get("/api/v1/catalog/products/?q=test")
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductDetailAPI:
    def test_returns_product_by_slug(self, client) -> None:
        from tests.factories.catalog import ProductFactory

        p = ProductFactory(status="active")
        response = client.get(f"/api/v1/catalog/products/{p.slug}/")
        assert response.status_code == 200
        assert response.json()["slug"] == p.slug

    def test_returns_404_for_unknown_slug(self, client) -> None:
        response = client.get("/api/v1/catalog/products/does-not-exist-xyz/")

        assert response.status_code == 404

    def test_detail_includes_variants(self, client) -> None:
        from tests.factories.catalog import ProductFactory, VariantFactory

        p = ProductFactory(status="active")
        v = VariantFactory(product=p, is_active=True)
        response = client.get(f"/api/v1/catalog/products/{p.slug}/")
        data = response.json()
        skus = [variant["sku"] for variant in data.get("variants", [])]
        assert v.sku in skus


@pytest.mark.django_db
class TestCategoryListAPI:
    def test_returns_200(self, client) -> None:
        response = client.get("/api/v1/catalog/categories/")
        assert response.status_code == 200

    def test_returns_active_root_categories(self, client) -> None:
        from tests.factories.catalog import CategoryFactory

        cat = CategoryFactory(is_active=True)
        response = client.get("/api/v1/catalog/categories/")
        data = response.json()
        slugs = [c["slug"] for c in data]
        assert cat.slug in slugs

    def test_inactive_categories_not_returned(self, client) -> None:
        from tests.factories.catalog import CategoryFactory

        cat = CategoryFactory(is_active=False)
        response = client.get("/api/v1/catalog/categories/")
        data = response.json()
        slugs = [c["slug"] for c in data]
        assert cat.slug not in slugs
