from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ["action", "target_type", "target_id", "actor", "created_at"]
    list_filter = ["action", "target_type"]
    search_fields = ["actor__email", "target_id", "action"]
    readonly_fields = ["actor", "action", "target_type", "target_id", "payload", "created_at"]

    def has_add_permission(self, request):  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None):  # type: ignore[override]
        return False
