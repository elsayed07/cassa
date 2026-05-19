from __future__ import annotations

import uuid

from django.db import transaction

from apps.inventory.models import StockItem, StockMovement
from shared.exceptions import StockError


class StockService:
    @staticmethod
    @transaction.atomic
    def reserve(variant_id: str, quantity: int, reservation_uuid: uuid.UUID | None = None) -> uuid.UUID:
        """Reserve `quantity` units. Returns the reservation UUID."""
        stock = StockItem.objects.select_for_update().get(variant_id=variant_id)
        if stock.available < quantity:
            raise StockError(
                f"Insufficient stock for variant {variant_id}: "
                f"available={stock.available}, requested={quantity}"
            )
        if reservation_uuid is None:
            reservation_uuid = uuid.uuid4()
        stock.quantity_reserved += quantity
        stock.save(update_fields=["quantity_reserved"])
        StockMovement.objects.create(
            stock_item=stock,
            type=StockMovement.Type.RESERVE,
            quantity=quantity,
            reservation_uuid=reservation_uuid,
        )
        return reservation_uuid

    @staticmethod
    @transaction.atomic
    def release(reservation_uuid: uuid.UUID) -> None:
        """Release a previously made reservation."""
        movements = StockMovement.objects.filter(
            reservation_uuid=reservation_uuid,
            type=StockMovement.Type.RESERVE,
        ).select_related("stock_item")
        for movement in movements:
            stock = StockItem.objects.select_for_update().get(pk=movement.stock_item_id)
            stock.quantity_reserved = max(0, stock.quantity_reserved - movement.quantity)
            stock.save(update_fields=["quantity_reserved"])
            StockMovement.objects.create(
                stock_item=stock,
                type=StockMovement.Type.RELEASE,
                quantity=movement.quantity,
                reservation_uuid=reservation_uuid,
            )

    @staticmethod
    @transaction.atomic
    def commit(reservation_uuid: uuid.UUID) -> None:
        """Convert a reservation to a completed sale."""
        movements = StockMovement.objects.filter(
            reservation_uuid=reservation_uuid,
            type=StockMovement.Type.RESERVE,
        ).select_related("stock_item")
        for movement in movements:
            stock = StockItem.objects.select_for_update().get(pk=movement.stock_item_id)
            stock.quantity_on_hand = max(0, stock.quantity_on_hand - movement.quantity)
            stock.quantity_reserved = max(0, stock.quantity_reserved - movement.quantity)
            stock.save(update_fields=["quantity_on_hand", "quantity_reserved"])
            StockMovement.objects.create(
                stock_item=stock,
                type=StockMovement.Type.SALE,
                quantity=movement.quantity,
                reservation_uuid=reservation_uuid,
            )
