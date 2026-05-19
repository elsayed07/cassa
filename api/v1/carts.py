from __future__ import annotations

from typing import Any

from ninja import Router, Schema

from apps.carts.services.cart import CartService

router = Router()


class AddItemIn(Schema):
    variant_id: str
    quantity: int = 1


@router.get("/", response=dict)
def get_cart(request: Any) -> dict:
    cart = CartService.get_or_create_for_user(request.auth)
    return {
        "id": str(cart.id),
        "item_count": cart.item_count,
        "subtotal": float(cart.subtotal),
        "currency": cart.currency,
        "items": [
            {
                "variant_id": str(i.variant_id),
                "sku": i.variant.sku,
                "quantity": i.quantity,
                "unit_price": float(i.unit_price),
                "line_total": float(i.line_total),
            }
            for i in cart.items.select_related("variant")
        ],
    }


@router.post("/items/", response=dict)
def add_item(request: Any, payload: AddItemIn) -> dict:
    from shared.exceptions import CartError, StockError
    from ninja.errors import HttpError

    cart = CartService.get_or_create_for_user(request.auth)
    try:
        CartService.add(cart, payload.variant_id, payload.quantity)
    except (CartError, StockError) as exc:
        raise HttpError(400, str(exc))

    return {"item_count": cart.item_count}


@router.delete("/items/{variant_id}/", response=dict)
def remove_item(request: Any, variant_id: str) -> dict:
    cart = CartService.get_or_create_for_user(request.auth)
    CartService.remove(cart, variant_id)
    return {"item_count": cart.item_count}
