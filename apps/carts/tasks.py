from celery import shared_task


@shared_task(name="carts.sweep_abandoned_carts")
def sweep_abandoned_carts() -> None:
    from datetime import timedelta

    from django.utils import timezone

    from apps.carts.models import Cart
    from apps.notifications.services import NotificationService

    cutoff = timezone.now() - timedelta(hours=4)
    abandoned = Cart.objects.filter(
        user__isnull=False,
        items__isnull=False,
        updated_at__lt=cutoff,
        recovery_email_sent_at__isnull=True,
    ).distinct().select_related("user")

    for cart in abandoned:
        NotificationService.send_abandoned_cart(cart)
        cart.recovery_email_sent_at = timezone.now()
        cart.save(update_fields=["recovery_email_sent_at"])
