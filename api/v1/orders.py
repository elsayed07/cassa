from __future__ import annotations

from typing import Any

from ninja import Router

from apps.orders.selectors import OrderSelector

router = Router()


@router.get("/", response=list)
def list_orders(request: Any) -> list:
    orders = OrderSelector.for_user(request.auth)
    return [
        {
            "id": str(o.id),
            "number": o.number,
            "status": o.status,
            "grand_total": float(o.grand_total),
            "currency": o.currency,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@router.get("/{number}/", response=dict)
def order_detail(request: Any, number: str) -> dict:
    from shared.exceptions import NotFoundError
    from ninja.errors import HttpError

    try:
        order = OrderSelector.by_number(number)
    except NotFoundError as exc:
        raise HttpError(404, str(exc))

    if order.user_id != request.auth.id:
        raise HttpError(403, "Forbidden")

    return {
        "id": str(order.id),
        "number": order.number,
        "status": order.status,
        "grand_total": float(order.grand_total),
        "items": [
            {"sku": i.sku, "quantity": i.quantity, "unit_price": float(i.unit_price)}
            for i in order.items.all()
        ],
    }
