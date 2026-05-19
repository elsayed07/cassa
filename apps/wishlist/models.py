from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.catalog.models.product import Product
from shared.models import BaseModel


class Wishlist(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist"
    )

    class Meta(BaseModel.Meta):
        db_table = "wishlist_wishlist"

    def __str__(self) -> str:
        return f"Wishlist({self.user})"


class WishlistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_item"
        unique_together = [["wishlist", "product"]]

    def __str__(self) -> str:
        return f"{self.product} in {self.wishlist}"
