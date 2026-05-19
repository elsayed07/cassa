from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("cassa")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "sweep-abandoned-carts": {
        "task": "apps.carts.tasks.sweep_abandoned_carts",
        "schedule": crontab(minute=0, hour="*"),  # every hour
    },
    "update-recommendation-scores": {
        "task": "apps.recommendations.tasks.update_scores",
        "schedule": crontab(minute=0, hour=2),  # daily at 02:00 UTC
    },
    "rollup-daily-analytics": {
        "task": "apps.analytics.tasks.rollup_daily",
        "schedule": crontab(minute=0, hour=1),  # daily at 01:00 UTC
    },
    "release-expired-stock-reservations": {
        "task": "apps.inventory.tasks.release_expired_reservations",
        "schedule": crontab(minute="*/15"),  # every 15 minutes
    },
}
