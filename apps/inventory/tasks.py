from celery import shared_task


@shared_task(name="inventory.release_expired_reservations")
def release_expired_reservations() -> None:
    """Release stock reservations for orders stuck in awaiting_payment for too long."""
    from django.utils import timezone
    from datetime import timedelta

    from apps.orders.models import Order
    from apps.inventory.services.stock import StockService

    cutoff = timezone.now() - timedelta(hours=2)
    expired_orders = Order.objects.filter(
        status=Order.Status.AWAITING_PAYMENT,
        created_at__lt=cutoff,
        reservation_uuid__isnull=False,
    )
    for order in expired_orders:
        StockService.release(order.reservation_uuid)
        order.cancel()
