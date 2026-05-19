from celery import shared_task


@shared_task(name="recommendations.update_recommendation_scores")
def update_recommendation_scores(order_id: str) -> None:
    from apps.orders.models import OrderItem

    product_ids = list(
        OrderItem.objects.filter(order_id=order_id).values_list("variant__product_id", flat=True)
    )
    product_id_strs = [str(pid) for pid in product_ids if pid]

    from apps.recommendations.services import RecommendationService
    RecommendationService.record_purchase(product_id_strs)


@shared_task(name="recommendations.update_scores")
def update_scores() -> None:
    """Periodic task placeholder for bulk score recalculation if needed."""
    pass
