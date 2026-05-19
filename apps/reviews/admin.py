from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ["product", "user", "rating", "status", "created_at"]
    list_filter = ["status", "rating"]
    search_fields = ["user__email", "product__translations__name"]
    actions = ["approve_reviews", "reject_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):  # type: ignore[override]
        queryset.update(status=Review.Status.APPROVED)
        from shared.cache import CacheKey
        from django.core.cache import cache
        for review in queryset:
            cache.delete(CacheKey.review_aggregate(str(review.product_id)))

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):  # type: ignore[override]
        queryset.update(status=Review.Status.REJECTED)
