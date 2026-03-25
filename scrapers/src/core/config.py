"""Scraper configuration loaded from environment variables."""

from pydantic import Field
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


def load_settings() -> ScraperSettings:
    return ScraperSettings()
