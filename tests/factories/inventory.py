import factory

from apps.inventory.models import StockItem
from tests.factories.catalog import VariantFactory


class StockItemFactory(factory.django.DjangoModelFactory):
    variant = factory.SubFactory(VariantFactory)
    quantity_on_hand = 10
    quantity_reserved = 0

    class Meta:
        model = StockItem
