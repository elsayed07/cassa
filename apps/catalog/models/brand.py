from __future__ import annotations

from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields

from apps.catalog.models.managers import (
    AllObjectsTranslatableManager,
    SoftDeleteTranslatableManager,
)
from shared.models import BaseModel


class Brand(BaseModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
    )
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteTranslatableManager()
    all_objects = AllObjectsTranslatableManager()

    class Meta(BaseModel.Meta):
        db_table = "catalog_brand"

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            name = self.safe_translation_getter("name", any_language=True) or ""
            self.slug = slugify(name)
        super().save(*args, **kwargs)
