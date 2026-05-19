from __future__ import annotations

from django.conf import settings
from django.db import models

from shared.models import BaseModel


class Address(BaseModel):
    class Type(models.TextChoices):
        BILLING = "billing", "Billing"
        SHIPPING = "shipping", "Shipping"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.SHIPPING)
    full_name = models.CharField(max_length=200)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2)  # ISO 3166-1 alpha-2
    phone = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "accounts_address"
        indexes = [
            models.Index(fields=["user", "type", "is_default"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name}, {self.line1}, {self.city}"

    def as_dict(self) -> dict[str, str]:
        return {
            "full_name": self.full_name,
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "phone": self.phone,
        }
