from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.coupons.models import Coupon, CouponRedemption


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ["code", "discount_type", "value", "valid_from", "valid_to", "max_uses", "is_active"]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["code"]


@admin.register(CouponRedemption)
class CouponRedemptionAdmin(ModelAdmin):
    list_display = ["coupon", "user", "order", "redeemed_at", "discount_applied"]
    list_filter = ["coupon"]
    raw_id_fields = ["order"]
