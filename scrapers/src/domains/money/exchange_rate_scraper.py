"""Shared exchange-rate scraper foundation entrypoint."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.base_scraper import BaseScraper
from src.domains.money.fx_models import (
    NormalizedFxObservation,
    PersistObservationResult,
)
from src.domains.money.fx_persistence import ExchangeRatePersistenceStore


class ExchangeRateScraper(BaseScraper, ABC):
    """Base class for concrete BOT, CRDB, and NMB exchange-rate scrapers."""

    source_slug: str

    def __init__(
        self,
        persistence_store: ExchangeRatePersistenceStore | None = None,
    ) -> None:
        self._persistence_store = persistence_store

    @abstractmethod
    def collect_observations(self) -> list[NormalizedFxObservation]:
        """Fetch and normalize source observations for persistence."""

    def persist_observations(
        self,
        observations: list[NormalizedFxObservation],
    ) -> PersistObservationResult:
        if self._persistence_store is None:
            return PersistObservationResult(skipped=len(observations))
        return self._persistence_store.persist_observations(observations)

    def run(self) -> None:
        observations = self.collect_observations()
        self.persist_observations(observations)
