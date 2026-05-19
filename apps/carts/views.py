from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.carts.services.cart import CartService
from shared.exceptions import CartError, CouponError, StockError


def _get_cart(request: HttpRequest):  # type: ignore[return]
    if request.user.is_authenticated:
        return CartService.get_or_create_for_user(request.user)
    if not request.session.session_key:
        request.session.create()
    return CartService.get_or_create_for_session(request.session.session_key)


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    return render(request, "pages/cart/detail.html", {"cart": cart})


@require_POST
def add_to_cart(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    variant_id = request.POST.get("variant_id", "")
    quantity = int(request.POST.get("quantity", 1))

    error = None
    try:
        CartService.add(cart, variant_id, quantity)
    except (CartError, StockError) as exc:
        error = str(exc)

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/cart_drawer.html", {
            "cart": cart,
            "error": error,
        })
    return render(request, "pages/cart/detail.html", {"cart": cart, "error": error})


@require_POST
def update_cart(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    variant_id = request.POST.get("variant_id", "")
    quantity = int(request.POST.get("quantity", 0))

    try:
        CartService.update_quantity(cart, variant_id, quantity)
    except (CartError, StockError):
        pass

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/cart_drawer.html", {"cart": cart})
    return render(request, "pages/cart/detail.html", {"cart": cart})


@require_POST
def remove_from_cart(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    variant_id = request.POST.get("variant_id", "")
    CartService.remove(cart, variant_id)

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/cart_drawer.html", {"cart": cart})
    return render(request, "pages/cart/detail.html", {"cart": cart})


@require_POST
def apply_coupon(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    code = request.POST.get("code", "")
    error = None

    try:
        CartService.apply_coupon(cart, code, request.user if request.user.is_authenticated else None)
    except CouponError as exc:
        error = str(exc)

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/coupon_input.html", {"cart": cart, "error": error})
    return render(request, "pages/cart/detail.html", {"cart": cart, "error": error})


@require_POST
def remove_coupon(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    CartService.remove_coupon(cart)

    if request.htmx:  # type: ignore[attr-defined]
        return render(request, "components/coupon_input.html", {"cart": cart})
    return render(request, "pages/cart/detail.html", {"cart": cart})
