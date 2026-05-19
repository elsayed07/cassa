"""
Seed the database with realistic development data.

Usage:
    python manage.py seed
    python manage.py seed --flush   # wipe all data first
"""

from __future__ import annotations

import random
import uuid
from decimal import Decimal

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Populate the database with development seed data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding (dev only)",
        )

    def handle(self, *args, **options):
        from django.conf import settings as django_settings

        if django_settings.DEBUG is False and not django_settings.TESTING:
            raise CommandError("Seed is only allowed in DEBUG or TESTING mode.")

        if options["flush"]:
            self._flush()

        with transaction.atomic():
            self._seed_site()
            staff, customer = self._seed_users()
            brands = self._seed_brands()
            categories = self._seed_categories()
            products = self._seed_products(brands, categories)
            self._seed_coupons()
            self._seed_wishlist(customer, products)

        self.stdout.write(self.style.SUCCESS("Seed complete."))

    # ------------------------------------------------------------------
    def _flush(self):
        from apps.accounts.models import User
        from apps.catalog.models import Brand, Category, Product
        from apps.coupons.models import Coupon

        User.objects.filter(is_superuser=False).delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Coupon.objects.all().delete()
        self.stdout.write("Flushed existing data.")

    def _seed_site(self):
        site, _ = Site.objects.update_or_create(
            id=1, defaults={"domain": "localhost:8000", "name": "Cassa Dev"}
        )

    def _seed_users(self):
        from apps.accounts.models import User

        staff, _ = User.objects.get_or_create(
            email="staff@cassa.dev",
            defaults={
                "first_name": "Staff",
                "last_name": "User",
                "is_staff": True,
                "is_active": True,
            },
        )
        staff.set_password("staffpass123")
        staff.save()

        customer, _ = User.objects.get_or_create(
            email="customer@cassa.dev",
            defaults={
                "first_name": "Jane",
                "last_name": "Smith",
                "is_active": True,
            },
        )
        customer.set_password("customerpass123")
        customer.save()

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email="admin@cassa.dev",
                password="adminpass123",
                first_name="Admin",
                last_name="User",
            )

        self.stdout.write(f"  Users: admin@cassa.dev / staff@cassa.dev / customer@cassa.dev")
        return staff, customer

    def _seed_brands(self):
        from apps.catalog.models import Brand

        brand_names = ["Aria", "Nomad", "Ember", "Solace", "Drift"]
        brands = []
        for name in brand_names:
            slug = name.lower()
            if Brand.objects.filter(slug=slug).exists():
                brands.append(Brand.objects.get(slug=slug))
                continue
            brand = Brand(slug=slug, is_active=True)
            brand.set_current_language("en")
            brand.name = name
            brand.save()
            brands.append(brand)
        self.stdout.write(f"  Brands: {len(brands)}")
        return brands

    def _seed_categories(self):
        from apps.catalog.models import Category

        root_data = [
            ("Clothing", "clothing"),
            ("Footwear", "footwear"),
            ("Accessories", "accessories"),
        ]
        sub_data = {
            "clothing": [("T-Shirts", "t-shirts"), ("Jackets", "jackets"), ("Denim", "denim")],
            "footwear": [("Sneakers", "sneakers"), ("Boots", "boots")],
            "accessories": [("Bags", "bags"), ("Hats", "hats"), ("Watches", "watches")],
        }

        categories = []
        for name, slug in root_data:
            if Category.objects.filter(slug=slug).exists():
                root = Category.objects.get(slug=slug)
            else:
                root = Category.add_root(slug=slug, is_active=True)
                root.set_current_language("en")
                root.name = name
                root.save()
            categories.append(root)
            for sub_name, sub_slug in sub_data.get(slug, []):
                if Category.objects.filter(slug=sub_slug).exists():
                    sub = Category.objects.get(slug=sub_slug)
                else:
                    sub = root.add_child(slug=sub_slug, is_active=True)
                    sub.set_current_language("en")
                    sub.name = sub_name
                    sub.save()
                categories.append(sub)

        self.stdout.write(f"  Categories: {len(categories)}")
        return categories

    def _seed_products(self, brands, categories):
        from apps.catalog.models import Product, ProductVariant
        from apps.inventory.models import StockItem

        adjectives = ["Classic", "Modern", "Urban", "Vintage", "Premium", "Essential", "Slim"]
        nouns = ["Tee", "Jacket", "Sneaker", "Boot", "Bag", "Cap", "Watch"]
        products = []

        for i in range(15):
            name = f"{random.choice(adjectives)} {random.choice(nouns)}"
            slug = f"{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
            brand = random.choice(brands)
            category = random.choice(categories)
            base_price = Decimal(random.randint(2999, 24999)) / 100

            product = Product(
                slug=slug,
                brand=brand,
                category=category,
                status=Product.Status.ACTIVE,
                is_featured=i < 3,
                base_price=base_price,
            )
            product.set_current_language("en")
            product.name = name
            product.save()
            products.append(product)

            for size in ["S", "M", "L"]:
                sku = f"{str(product.pk)[:8].upper()}-{size}"
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=sku,
                    price=base_price,
                    is_active=True,
                    attributes={"size": size},
                )
                StockItem.objects.create(
                    variant=variant,
                    quantity_on_hand=random.randint(5, 50),
                )

        self.stdout.write(f"  Products: {len(products)} (with variants + stock)")
        return products

    def _seed_coupons(self):
        from django.utils import timezone

        from apps.coupons.models import Coupon

        now = timezone.now()
        valid_from = now
        valid_to = now.replace(year=now.year + 1)

        coupons_data = [
            {
                "code": "WELCOME10",
                "discount_type": Coupon.DiscountType.PERCENTAGE,
                "value": Decimal("10.00"),
                "max_uses": 1000,
                "max_uses_per_user": 1,
                "valid_from": valid_from,
                "valid_to": valid_to,
            },
            {
                "code": "SAVE20",
                "discount_type": Coupon.DiscountType.FIXED,
                "value": Decimal("20.00"),
                "min_subtotal": Decimal("100.00"),
                "max_uses": 500,
                "max_uses_per_user": 1,
                "valid_from": valid_from,
                "valid_to": valid_to,
            },
            {
                "code": "FREESHIP",
                "discount_type": Coupon.DiscountType.FREE_SHIPPING,
                "value": Decimal("0.00"),
                "max_uses": 200,
                "valid_from": valid_from,
                "valid_to": valid_to,
            },
        ]
        for data in coupons_data:
            Coupon.objects.get_or_create(code=data.pop("code"), defaults=data)

        self.stdout.write("  Coupons: WELCOME10 / SAVE20 / FREESHIP")

    def _seed_wishlist(self, customer, products):
        if not products:
            return
        from apps.wishlist.models import Wishlist, WishlistItem

        wishlist, _ = Wishlist.objects.get_or_create(user=customer)
        for product in products[:3]:
            WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        self.stdout.write("  Wishlist: 3 items for customer@cassa.dev")
