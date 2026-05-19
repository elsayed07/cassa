from __future__ import annotations

import uuid

import pytest

from shared.exceptions import StockError


@pytest.mark.django_db(transaction=True)
class TestStockServiceReserve:
    def test_reserve_reduces_available(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=10, quantity_reserved=0)
        StockService.reserve(str(stock.variant_id), 3)

        stock.refresh_from_db()
        assert stock.quantity_reserved == 3
        assert stock.available == 7

    def test_reserve_returns_uuid(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=5)
        reservation_uuid = StockService.reserve(str(stock.variant_id), 2)
        assert isinstance(reservation_uuid, uuid.UUID)

    def test_reserve_uses_provided_uuid(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=5)
        given_uuid = uuid.uuid4()
        returned_uuid = StockService.reserve(str(stock.variant_id), 1, reservation_uuid=given_uuid)
        assert returned_uuid == given_uuid

    def test_reserve_raises_on_insufficient_stock(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=2, quantity_reserved=0)
        with pytest.raises(StockError, match="Insufficient stock"):
            StockService.reserve(str(stock.variant_id), 5)

    def test_reserve_raises_when_all_stock_reserved(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=3, quantity_reserved=3)
        with pytest.raises(StockError):
            StockService.reserve(str(stock.variant_id), 1)


@pytest.mark.django_db(transaction=True)
class TestStockServiceRelease:
    def test_release_restores_reserved_quantity(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=10)
        reservation_uuid = StockService.reserve(str(stock.variant_id), 4)

        stock.refresh_from_db()
        assert stock.quantity_reserved == 4

        StockService.release(reservation_uuid)
        stock.refresh_from_db()
        assert stock.quantity_reserved == 0
        assert stock.available == 10

    def test_release_unknown_uuid_is_noop(self) -> None:
        from apps.inventory.services.stock import StockService

        # Should not raise for an unknown reservation UUID
        StockService.release(uuid.uuid4())


@pytest.mark.django_db(transaction=True)
class TestStockServiceCommit:
    def test_commit_decrements_on_hand_and_reserved(self) -> None:
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=10)
        reservation_uuid = StockService.reserve(str(stock.variant_id), 3)
        StockService.commit(reservation_uuid)

        stock.refresh_from_db()
        assert stock.quantity_on_hand == 7
        assert stock.quantity_reserved == 0

    def test_commit_creates_sale_movement(self) -> None:
        from apps.inventory.models import StockMovement
        from apps.inventory.services.stock import StockService
        from tests.factories.inventory import StockItemFactory

        stock = StockItemFactory(quantity_on_hand=5)
        reservation_uuid = StockService.reserve(str(stock.variant_id), 2)
        StockService.commit(reservation_uuid)

        assert StockMovement.objects.filter(
            reservation_uuid=reservation_uuid,
            type=StockMovement.Type.SALE,
        ).exists()
