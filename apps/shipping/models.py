from __future__ import annotations

from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.db import models

from shared.models import BaseModel


class ShippingZone(BaseModel):
    name = models.CharField(max_length=200)
    countries = ArrayField(models.CharField(max_length=2), help_text="ISO 3166-1 alpha-2 codes")
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "shipping_zone"

    def __str__(self) -> str:
        return self.name


class ShippingMethod(BaseModel):
    class RateType(models.TextChoices):
        FLAT = "flat", "Flat Rate"
        WEIGHT = "weight", "Weight-Based"
        FREE = "free", "Free"

    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name="methods")
    name = models.CharField(max_length=200)
    rate_type = models.CharField(max_length=10, choices=RateType.choices, default=RateType.FLAT)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    min_days = models.PositiveSmallIntegerField(default=3)
    max_days = models.PositiveSmallIntegerField(default=7)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        db_table = "shipping_method"

    def __str__(self) -> str:
        return f"{self.name} ({self.zone})"

    def calculate_rate(self, weight_kg: Decimal = Decimal("0")) -> Decimal:
        if self.rate_type == self.RateType.FREE:
            return Decimal("0")
        if self.rate_type == self.RateType.FLAT:
            return self.base_rate
        return self.base_rate + (weight_kg * self.per_kg_rate)
