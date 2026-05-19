from __future__ import annotations

from typing import Any

from apps.accounts.models import Address, User


class AddressService:
    @staticmethod
    def create(user: User, data: dict[str, Any]) -> Address:
        if data.get("is_default"):
            Address.objects.filter(user=user, type=data.get("type")).update(is_default=False)
        return Address.objects.create(user=user, **data)

    @staticmethod
    def update(address: Address, data: dict[str, Any]) -> Address:
        if data.get("is_default"):
            Address.objects.filter(user=address.user, type=data.get("type", address.type)).exclude(
                pk=address.pk
            ).update(is_default=False)
        for field, value in data.items():
            setattr(address, field, value)
        address.save()
        return address
