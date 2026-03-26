"""Abstract base class for domain scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Domain scrapers implement ``run`` for Celery/orchestration entrypoints."""

    name: str

    @abstractmethod
    def run(self) -> None:
        """Execute the scraper (fetch, parse, persist when applicable)."""
