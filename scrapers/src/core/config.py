"""Scraper configuration loaded from environment variables."""

from datetime import datetime, timezone

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ewura_listing_url: str = Field(
        default="https://www.ewura.go.tz/pages/petroleum-product-pricing",
        description="HTML page listing petroleum cap price PDFs/DOCX",
    )
    bot_exchange_rates_url: str = Field(
        default="https://www.bot.go.tz/exchangerate/excrates",
        description="Bank of Tanzania daily exchange-rates table page.",
    )
    http_timeout_seconds: float = Field(
        default=45.0,
        ge=1.0,
        le=300.0,
        description="HTTP client timeout for page fetches",
    )
    user_agent: str = Field(
        default="AQ-DataIntelligenceHub/1.0 (research; contact: admin@local)",
        description="User-Agent sent with outbound requests",
    )
    ewura_max_document_mb: float = Field(
        default=25.0,
        ge=1.0,
        le=200.0,
        description="Abort in-memory download if Content-Length or stream exceeds this",
    )
    ewura_run_pdf_limit: int | None = Field(
        default=None,
        ge=1,
        description=(
            "When set, ``EwuraFuelScraper.run`` ingests at most this many "
            "PDF/DOCX bulletins (name kept for backward compatibility)"
        ),
    )
    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "SCRAPER_DATABASE_URL"),
        description="PostgreSQL URL for fingerprint dedupe (optional)",
    )
    ewura_skip_successful_urls: bool = Field(
        default=False,
        description="Skip URLs that already have parse_ok=true in fingerprints",
    )
    ewura_min_year: int = Field(
        default=2025,
        ge=2000,
        le=2100,
        description="Ignore EWURA documents older than this year.",
    )
    ewura_max_year: int = Field(
        default_factory=lambda: datetime.now(timezone.utc).year,
        ge=2000,
        le=2100,
        description="Ignore EWURA documents newer than this year.",
    )
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("CELERY_BROKER_URL", "REDIS_URL"),
    )


def load_settings() -> ScraperSettings:
    return ScraperSettings()
