from __future__ import annotations

from django.http import HttpRequest

from apps.carts.services.cart import CartService


def cart(request: HttpRequest) -> dict:
    if request.user.is_authenticated:
        cart_obj = CartService.get_or_create_for_user(request.user)
    elif hasattr(request, "session") and request.session.session_key:
        cart_obj = CartService.get_or_create_for_session(request.session.session_key)
    else:
        return {"cart": None, "cart_item_count": 0}

    return {
        "cart": cart_obj,
        "cart_item_count": cart_obj.item_count,
    }
