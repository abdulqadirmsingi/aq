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


def load_settings() -> ScraperSettings:
    return ScraperSettings()
