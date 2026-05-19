from django.conf import settings
from django.db import models

from shared.models.base import BaseModel


class NotificationType(models.TextChoices):
    ORDER_CONFIRMATION = "order_confirmation", "Order Confirmation"
    ORDER_FULFILLED = "order_fulfilled", "Order Fulfilled"
    ORDER_CANCELLED = "order_cancelled", "Order Cancelled"
    PAYMENT_FAILED = "payment_failed", "Payment Failed"
    REFUND_ISSUED = "refund_issued", "Refund Issued"
    PASSWORD_RESET = "password_reset", "Password Reset"
    ABANDONED_CART = "abandoned_cart", "Abandoned Cart"
    REVIEW_APPROVED = "review_approved", "Review Approved"
    LOW_STOCK_ALERT = "low_stock_alert", "Low Stock Alert"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class NotificationLog(BaseModel):
    """Audit trail for every outbound notification attempt."""

    notification_type = models.CharField(
        max_length=50, choices=NotificationType.choices, db_index=True
    )
    status = models.CharField(
        max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    # Reference to the triggering object (order_id, etc.)
    object_id = models.UUIDField(null=True, blank=True)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["notification_type", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.notification_type} → {self.recipient_email} ({self.status})"
