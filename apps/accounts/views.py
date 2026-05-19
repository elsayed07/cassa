from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import Address
from apps.accounts.services.address import AddressService


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/account/dashboard.html")


@login_required
def order_list(request: HttpRequest) -> HttpResponse:
    from apps.orders.selectors import OrderSelector

    orders = OrderSelector.for_user(request.user)
    return render(request, "pages/account/orders.html", {"orders": orders})


@login_required
def order_detail(request: HttpRequest, order_id: str) -> HttpResponse:
    from apps.orders.selectors import OrderSelector

    order = get_object_or_404(OrderSelector.for_user(request.user), id=order_id)
    return render(request, "pages/account/order_detail.html", {"order": order})


@login_required
def wishlist(request: HttpRequest) -> HttpResponse:
    from apps.wishlist.selectors import WishlistSelector

    items = WishlistSelector.for_user(request.user)
    return render(request, "pages/account/wishlist.html", {"items": items})


@login_required
def address_list(request: HttpRequest) -> HttpResponse:
    addresses = Address.objects.filter(user=request.user)
    return render(request, "pages/account/addresses.html", {"addresses": addresses})


@login_required
def address_add(request: HttpRequest) -> HttpResponse:
    from apps.accounts.forms import AddressForm

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            AddressService.create(user=request.user, data=form.cleaned_data)
            return redirect("accounts:address-list")
    else:
        form = AddressForm()
    return render(request, "pages/account/address_form.html", {"form": form})


@login_required
def address_edit(request: HttpRequest, pk: str) -> HttpResponse:
    from apps.accounts.forms import AddressForm

    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            AddressService.update(address=address, data=form.cleaned_data)
            return redirect("accounts:address-list")
    else:
        form = AddressForm(instance=address)
    return render(request, "pages/account/address_form.html", {"form": form, "address": address})


@login_required
def address_delete(request: HttpRequest, pk: str) -> HttpResponse:
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        address.delete()
    return redirect("accounts:address-list")
