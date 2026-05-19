from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.orders.models import Order, OrderEvent, OrderItem, Refund


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["variant_id", "product_name", "sku", "unit_price", "quantity", "line_total"]
    can_delete = False


class OrderEventInline(TabularInline):
    model = OrderEvent
    extra = 0
    readonly_fields = ["status", "note", "created_by", "created_at"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "user", "status", "grand_total", "currency", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["number", "user__email"]
    readonly_fields = ["number", "reservation_uuid"]
    inlines = [OrderItemInline, OrderEventInline]


@admin.register(Refund)
class RefundAdmin(ModelAdmin):
    list_display = ["order", "amount", "status", "issued_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["order__number", "provider_refund_id"]
