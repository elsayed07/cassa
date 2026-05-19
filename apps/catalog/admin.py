from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin, TabularInline

from apps.catalog.models import Brand, Category, Product, ProductImage, ProductVariant


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ["sku", "name", "attributes", "price", "compare_at_price", "is_active", "position"]


@admin.register(Product)
class ProductAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ["__str__", "category", "brand", "status", "is_featured", "base_price", "created_at"]
    list_filter = ["status", "is_featured", "category", "brand"]
    search_fields = ["translations__name", "slug"]
    inlines = [ProductVariantInline, ProductImageInline]
    prepopulated_fields = {"slug": ()}

    def get_prepopulated_fields(self, request, obj=None):  # type: ignore[override]
        return {}


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ["__str__", "slug", "is_active", "sort_order"]
    search_fields = ["translations__name", "slug"]


@admin.register(Brand)
class BrandAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ["__str__", "slug", "is_active"]
    search_fields = ["translations__name", "slug"]
