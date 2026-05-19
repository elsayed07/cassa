from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.carts.services.cart import CartService
from apps.orders.models import Order
from apps.orders.services.checkout import CheckoutService
from shared.exceptions import CartError, StockError


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    cart = CartService.get_or_create_for_user(request.user)
    from apps.shipping.services.calculator import ShippingCalculator
    from apps.accounts.models import Address

    addresses = Address.objects.filter(user=request.user)
    default_shipping = addresses.filter(type="shipping", is_default=True).first()

    shipping_options: list = []
    if default_shipping:
        shipping_options = ShippingCalculator.options_for(cart, default_shipping.country)

    return render(request, "pages/checkout/checkout.html", {
        "cart": cart,
        "addresses": addresses,
        "shipping_options": shipping_options,
    })


@login_required
def order_confirm(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("orders:checkout")

    cart = CartService.get_or_create_for_user(request.user)
    from apps.accounts.models import Address
    from apps.shipping.models import ShippingMethod

    shipping_address_id = request.POST.get("shipping_address_id")
    billing_address_id = request.POST.get("billing_address_id", shipping_address_id)
    shipping_method_id = request.POST.get("shipping_method_id")

    try:
        shipping_address = Address.objects.get(pk=shipping_address_id, user=request.user)
        billing_address = Address.objects.get(pk=billing_address_id, user=request.user)
        shipping_method = ShippingMethod.objects.get(pk=shipping_method_id, is_active=True)
        order, intent = CheckoutService.create_order(
            cart=cart,
            shipping_address=shipping_address,
            billing_address=billing_address,
            shipping_method=shipping_method,
            user=request.user,
        )
    except (Address.DoesNotExist, ShippingMethod.DoesNotExist):
        return redirect("orders:checkout")
    except (CartError, StockError) as exc:
        return render(request, "pages/checkout/checkout.html", {"error": str(exc), "cart": cart})

    return render(request, "pages/checkout/payment.html", {
        "order": order,
        "client_secret": intent.client_secret,
    })


@login_required
def order_success(request: HttpRequest, order_number: str) -> HttpResponse:
    order = get_object_or_404(Order, number=order_number, user=request.user)
    return render(request, "pages/checkout/success.html", {"order": order})
