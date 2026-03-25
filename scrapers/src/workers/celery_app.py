"""Celery application for AQ scraper workers."""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from src.core.config import load_settings

_settings = load_settings()

app = Celery(
    "aq_scrapers",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_broker_url,
)
app.conf.update(
    task_default_queue="scrapers",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
app.conf.imports = ("src.workers.tasks",)
# EWURA publishes monthly; first day of month 07:00 UTC (adjust in Beat as needed).
app.conf.beat_schedule = {
    "ewura-fuel-monthly": {
        "task": "scrapers.run_ewura_fuel",
        "schedule": crontab(day_of_month="1", hour=7, minute=0),
    },
}


def main() -> None:
    app.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
        ],
    )


if __name__ == "__main__":
    main()
