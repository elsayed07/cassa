from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=100, db_index=True)
    target_id = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} on {self.target_type}:{self.target_id}"

    @classmethod
    def record(
        cls,
        action: str,
        target: object,
        actor: object = None,
        payload: dict | None = None,
    ) -> "AuditLog":
        return cls.objects.create(
            actor=actor,
            action=action,
            target_type=type(target).__name__,
            target_id=str(getattr(target, "id", "")),
            payload=payload or {},
        )
