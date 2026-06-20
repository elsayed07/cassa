from __future__ import annotations

from decimal import Decimal

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields

from apps.catalog.models.brand import Brand
from apps.catalog.models.category import Category
from apps.catalog.models.managers import (
    AllObjectsTranslatableManager,
    SoftDeleteTranslatableManager,
)
from shared.models import BaseModel


class Product(BaseModel, TranslatableModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    translations = TranslatedFields(
        name=models.CharField(max_length=400),
        description=models.TextField(blank=True),
        meta_title=models.CharField(max_length=200, blank=True),
        meta_description=models.TextField(blank=True),
    )
    slug = models.SlugField(max_length=400, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    objects = SoftDeleteTranslatableManager()
    all_objects = AllObjectsTranslatableManager()

    class Meta(BaseModel.Meta):
        db_table = "catalog_product"
        indexes = [
            GinIndex(fields=["search_vector"], name="catalog_product_search_idx"),
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            name = self.safe_translation_getter("name", any_language=True) or ""
            self.slug = slugify(name)
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE


class ProductVariant(BaseModel):
    """A specific sellable version of a Product (e.g. Size=M, Color=Blue)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    attributes = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta(BaseModel.Meta):
        db_table = "catalog_product_variant"
        ordering = ["position", "sku"]
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} — {self.sku}"

    @property
    def is_on_sale(self) -> bool:
        return self.compare_at_price is not None and self.compare_at_price > self.price

    @property
    def discount_percentage(self) -> Decimal | None:
        if self.compare_at_price and self.compare_at_price > self.price:
            return ((self.compare_at_price - self.price) / self.compare_at_price * 100).quantize(
                Decimal("1")
            )
        return None


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=300, blank=True)
    position = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        db_table = "catalog_product_image"
        ordering = ["position"]

    def __str__(self) -> str:
        return f"Image for {self.product} ({self.position})"
