from celery import shared_task


@shared_task(name="notifications.send_order_confirmation", bind=True, max_retries=3)
def send_order_confirmation(self, order_id: str) -> None:  # type: ignore[misc]
    try:
        from apps.notifications.services import NotificationService
        from apps.orders.models import Order

        order = Order.objects.select_related("user").prefetch_related("items").get(id=order_id)
        NotificationService.send_order_confirmation(order)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
