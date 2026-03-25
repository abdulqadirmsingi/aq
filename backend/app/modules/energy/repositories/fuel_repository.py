"""Main EWURA fuel repository composed from smaller query mixins."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.energy.repositories.fuel_repository_analytics import (
    FuelAnalyticsRepositoryMixin,
)
from app.modules.energy.repositories.fuel_repository_observations import (
    FuelObservationRepositoryMixin,
)
from app.modules.energy.repositories.fuel_repository_shared import (
    FuelAvailableMonthRecord,
    FuelLatestPriceRecord,
    FuelLatestSummaryRecord,
    FuelMonthlyTrendRecord,
    FuelObservationRecord,
)


class FuelRepository(FuelObservationRepositoryMixin, FuelAnalyticsRepositoryMixin):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
