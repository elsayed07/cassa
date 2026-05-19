from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.payments.models import PaymentIntent, WebhookEvent


@admin.register(PaymentIntent)
class PaymentIntentAdmin(ModelAdmin):
    list_display = ["provider_intent_id", "order", "provider", "status", "amount", "created_at"]
    list_filter = ["provider", "status"]
    search_fields = ["provider_intent_id", "order__number"]
    readonly_fields = ["provider_intent_id", "order", "provider"]


@admin.register(WebhookEvent)
class WebhookEventAdmin(ModelAdmin):
    list_display = ["provider_event_id", "event_type", "processed", "created_at"]
    list_filter = ["provider", "event_type", "processed"]
    search_fields = ["provider_event_id"]
    readonly_fields = ["provider_event_id", "provider", "payload"]
