"""Managers that make the catalog's translated models parler-compatible.

`parler.admin.TranslatableAdmin` requires the model's default-manager queryset to be a
`TranslatableQuerySet`. The catalog's translated models (Product, Brand, Category) carry
custom managers — `BaseModel`'s soft-delete manager and treebeard's `MP_NodeManager` —
whose querysets are plain `QuerySet`s, which shadow parler's manager and break the admin
changelist. These managers reinstate parler's queryset while preserving the original
soft-delete / tree behaviour.
"""

from __future__ import annotations

from parler.managers import TranslatableManager, TranslatableQuerySet
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet


class SoftDeleteTranslatableManager(TranslatableManager):
    """parler-aware default manager that hides soft-deleted rows (`BaseModel`)."""

    def get_queryset(self) -> TranslatableQuerySet:
        # super() returns a TranslatableQuerySet; .filter() preserves the class.
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsTranslatableManager(TranslatableManager):
    """parler-aware manager that includes soft-deleted rows (`BaseModel.all_objects`)."""


class TranslatableMPNodeQuerySet(MP_NodeQuerySet, TranslatableQuerySet):
    """Queryset that is both a treebeard MP_Node queryset and a parler one."""


class TranslatableMPNodeManager(TranslatableManager, MP_NodeManager):
    """treebeard MP_Node manager whose queryset is also a `TranslatableQuerySet`.

    treebeard's `MP_NodeManager.get_queryset` hard-codes `MP_NodeQuerySet`, so it has to
    be overridden to return the combined queryset (still ordered by `path`).
    """

    def get_queryset(self) -> TranslatableMPNodeQuerySet:
        return TranslatableMPNodeQuerySet(self.model, using=self._db).order_by("path")
