from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.wishlist.models import WishlistItem


class WishlistSelector:
    @staticmethod
    def for_user(user: "User") -> "QuerySet[WishlistItem]":
        from apps.wishlist.models import Wishlist, WishlistItem

        wishlist, _ = Wishlist.objects.get_or_create(user=user)
        return WishlistItem.objects.filter(wishlist=wishlist).select_related("product")
