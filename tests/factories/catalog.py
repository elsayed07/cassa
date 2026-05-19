import factory
from decimal import Decimal

from apps.catalog.models import Brand, Category, Product, ProductVariant


class BrandFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: f"brand-{n}")
    is_active = True

    class Meta:
        model = Brand


class CategoryFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: f"cat-{n}")
    is_active = True

    class Meta:
        model = Category

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.add_root(**kwargs)


class ProductFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    slug = factory.Sequence(lambda n: f"product-{n}")
    status = Product.Status.ACTIVE
    base_price = Decimal("29.99")
    currency = "USD"

    class Meta:
        model = Product


class VariantFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    price = Decimal("29.99")
    is_active = True

    class Meta:
        model = ProductVariant
