"""Fetch EWURA HTML listing pages."""

from src.core.http_client import ScraperHttpClient


def fetch_page(client: ScraperHttpClient, url: str) -> str:
    """Download page body as UTF-8 text (raises on HTTP errors)."""
    return client.get_text(url)
