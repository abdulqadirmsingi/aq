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
_EWURA_FUEL_BEAT_DAYS_UTC = (1, 3, 5, 8)
_EWURA_FUEL_BEAT_HOUR_UTC = 7
_EWURA_FUEL_BEAT_MINUTE = 0

app.conf.beat_schedule = {
    **{
        f"ewura-fuel-check-day-{day:02d}": {
            "task": "scrapers.run_ewura_fuel",
            "schedule": crontab(
                day_of_month=day,
                hour=_EWURA_FUEL_BEAT_HOUR_UTC,
                minute=_EWURA_FUEL_BEAT_MINUTE,
            ),
        }
        for day in _EWURA_FUEL_BEAT_DAYS_UTC
    },
    "bot-exchange-rates-nightly": {
        "task": "scrapers.run_bot_exchange_rates",
        "schedule": crontab(hour=22, minute=5),
    },
    "crdb-forex-nightly": {
        "task": "scrapers.run_crdb_forex",
        "schedule": crontab(hour=22, minute=20),
    },
    "nmb-daily-exchange-rates-nightly": {
        "task": "scrapers.run_nmb_daily_exchange_rates",
        "schedule": crontab(hour=22, minute=35),
    },
    "itrust-dse-stocks-daily": {
        "task": "scrapers.run_itrust_dse_stocks",
        # 13:00 UTC = ~16:00 EAT, after DSE closes at 15:00 EAT
        "schedule": crontab(hour=13, minute=0),
    },
    "nest-procurement-daily": {
        "task": "scrapers.run_nest_procurement",
        # 04:00 UTC = ~07:00 EAT — after OCDS daily refresh, before business hours
        "schedule": crontab(hour=4, minute=0),
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
