from celery import shared_task


@shared_task(name="orders.generate_invoice_pdf", bind=True, max_retries=3)
def generate_invoice_pdf(self, order_id: str) -> None:  # type: ignore[misc]
    try:
        from apps.orders.models import Order
        from apps.orders.services.invoice import InvoiceService

        order = Order.objects.prefetch_related("items").get(id=order_id)
        InvoiceService.generate_and_store(order)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
