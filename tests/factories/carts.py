import factory
from decimal import Decimal

from apps.carts.models import Cart, CartItem
from tests.factories.accounts import UserFactory
from tests.factories.catalog import VariantFactory


class CartFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Cart


class CartItemFactory(factory.django.DjangoModelFactory):
    cart = factory.SubFactory(CartFactory)
    variant = factory.SubFactory(VariantFactory)
    quantity = 1
    unit_price = Decimal("29.99")

    class Meta:
        model = CartItem
