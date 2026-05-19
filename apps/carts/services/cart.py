from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction

from apps.carts.models import Cart, CartItem
from apps.catalog.models.product import ProductVariant
from shared.exceptions import CartError, StockError

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.coupons.models import Coupon


class CartService:
    @staticmethod
    def get_or_create_for_user(user: "User") -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def get_or_create_for_session(session_key: str) -> Cart:
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @staticmethod
    @transaction.atomic
    def merge(session_key: str, user: "User") -> Cart:
        """Merge an anonymous session cart into the authenticated user's cart."""
        try:
            anonymous_cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            return CartService.get_or_create_for_user(user)

        user_cart, _ = Cart.objects.get_or_create(user=user)

        for item in anonymous_cart.items.all():
            existing = user_cart.items.filter(variant=item.variant).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=["quantity"])
            else:
                CartItem.objects.create(
                    cart=user_cart,
                    variant=item.variant,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

        anonymous_cart.session_key = None
        anonymous_cart.save(update_fields=["session_key"])
        anonymous_cart.delete()
        return user_cart

    @staticmethod
    def add(cart: Cart, variant_id: str, quantity: int = 1) -> CartItem:
        try:
            variant = ProductVariant.objects.select_related("stock", "product").get(
                id=variant_id, is_active=True
            )
        except ProductVariant.DoesNotExist:
            raise CartError("Product variant not found.")

        try:
            stock = variant.stock
            if stock.available < quantity:
                raise StockError(f"Only {stock.available} units available.")
        except AttributeError:
            raise StockError("Stock information unavailable.")

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "unit_price": variant.price},
        )
        if not created:
            new_qty = item.quantity + quantity
            if hasattr(variant, "stock") and variant.stock.available < new_qty:
                raise StockError(f"Only {variant.stock.available} units available.")
            item.quantity = new_qty
            item.save(update_fields=["quantity"])

        return item

    @staticmethod
    def update_quantity(cart: Cart, variant_id: str, quantity: int) -> CartItem | None:
        try:
            item = CartItem.objects.select_related("variant__stock").get(
                cart=cart, variant_id=variant_id
            )
        except CartItem.DoesNotExist:
            raise CartError("Item not in cart.")

        if quantity <= 0:
            item.delete()
            return None

        try:
            if item.variant.stock.available < quantity:
                raise StockError(f"Only {item.variant.stock.available} units available.")
        except AttributeError:
            pass

        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return item

    @staticmethod
    def remove(cart: Cart, variant_id: str) -> None:
        CartItem.objects.filter(cart=cart, variant_id=variant_id).delete()

    @staticmethod
    def apply_coupon(cart: Cart, code: str, user: "User | None") -> "Coupon":
        from apps.coupons.services.coupon import CouponService
        from shared.money import Money

        subtotal = Money(cart.subtotal, cart.currency)
        coupon = CouponService.validate(code, user, subtotal)
        cart.coupon = coupon
        cart.save(update_fields=["coupon"])
        return coupon

    @staticmethod
    def remove_coupon(cart: Cart) -> None:
        cart.coupon = None
        cart.save(update_fields=["coupon"])
