from __future__ import annotations

from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from treebeard.mp_tree import MP_Node

from apps.catalog.models.managers import TranslatableMPNodeManager


class Category(MP_Node, TranslatableModel):
    """Materialized-path category tree with translated names."""

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
        meta_title=models.CharField(max_length=200, blank=True),
        meta_description=models.TextField(blank=True),
    )
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)

    objects = TranslatableMPNodeManager()

    node_order_by = ["sort_order", "slug"]

    class Meta:
        db_table = "catalog_category"

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            name = self.safe_translation_getter("name", any_language=True) or ""
            self.slug = slugify(name)
        super().save(*args, **kwargs)
