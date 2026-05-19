from __future__ import annotations

from decimal import Decimal

from django.db import models

from shared.models import BaseModel


class TaxZone(BaseModel):
    name = models.CharField(max_length=200)
    countries = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "tax_zone"

    def __str__(self) -> str:
        return self.name


class TaxRate(BaseModel):
    zone = models.ForeignKey(TaxZone, on_delete=models.CASCADE, related_name="rates")
    name = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=6, decimal_places=4)
    is_inclusive = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "tax_rate"

    def __str__(self) -> str:
        return f"{self.name} ({self.rate * 100:.2f}%)"
