from django.db.models import Value
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.catalog.models.product import Product


@receiver(post_save, sender=Product)
def update_search_vector(sender: type[Product], instance: Product, **kwargs: object) -> None:
    from django.contrib.postgres.search import SearchVector

    # Read translated values in Python so the UPDATE stays join-free.
    name = instance.safe_translation_getter("name", any_language=True) or ""
    description = instance.safe_translation_getter("description", any_language=True) or ""

    Product.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector(Value(name), weight="A", config="english")
            + SearchVector(Value(description), weight="B", config="english")
        )
    )
