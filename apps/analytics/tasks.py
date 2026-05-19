from celery import shared_task


@shared_task(name="analytics.rollup_daily")
def rollup_daily() -> None:
    """Roll up yesterday's order/revenue data into a daily summary row."""
    pass
