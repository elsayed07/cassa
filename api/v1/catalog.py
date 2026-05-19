from __future__ import annotations

from typing import Any
from uuid import UUID

from ninja import Router, Schema

from apps.catalog.selectors import CategorySelector, ProductSelector
from shared.pagination import paginate

router = Router()


class ProductOut(Schema):
    id: UUID
    slug: str
    status: str
    base_price: float
    currency: str
    is_featured: bool


class CategoryOut(Schema):
    id: int
    slug: str
    is_active: bool


@router.get("/products/", response=dict, auth=None)
def list_products(request: Any, page: int = 1, q: str = "") -> dict:
    if q:
        qs = ProductSelector.search(q)
    else:
        qs = ProductSelector.active()
    result = paginate(qs, page=page)
    result["items"] = [
        {
            "id": str(p.id),
            "slug": p.slug,
            "status": p.status,
            "base_price": float(p.base_price),
            "currency": p.currency,
            "is_featured": p.is_featured,
        }
        for p in result["items"]
    ]
    return result


@router.get("/products/{slug}/", response=dict, auth=None)
def product_detail(request: Any, slug: str) -> dict:
    from shared.exceptions import NotFoundError
    from ninja.errors import HttpError

    try:
        product = ProductSelector.by_slug(slug)
    except NotFoundError as exc:
        raise HttpError(404, str(exc))

    return {
        "id": str(product.id),
        "slug": product.slug,
        "name": product.safe_translation_getter("name", any_language=True),
        "status": product.status,
        "currency": product.currency,
        "variants": [
            {"id": str(v.id), "sku": v.sku, "price": float(v.price), "name": v.name}
            for v in product.variants.filter(is_active=True)
        ],
    }


@router.get("/categories/", response=list, auth=None)
def list_categories(request: Any) -> list:
    categories = CategorySelector.active_roots()
    return [{"id": c.pk, "slug": c.slug, "name": str(c)} for c in categories]
