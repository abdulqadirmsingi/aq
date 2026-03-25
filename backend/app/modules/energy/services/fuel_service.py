"""Business logic for fuel data (EWURA cap prices)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.db.models.data_point import DataPoint
from app.modules.energy.repositories.fuel_repository import FuelRepository
from app.modules.energy.schemas.fuel import EwuraFuelObservationRead


class FuelService:
    def __init__(self, repository: FuelRepository) -> None:
        self._repository = repository

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
    ) -> list[EwuraFuelObservationRead]:
        rows = await self._repository.list_ewura_observations(
            limit=limit,
            offset=offset,
        )
        return [self._to_read_model(row) for row in rows]

    def _to_read_model(self, row: DataPoint) -> EwuraFuelObservationRead:
        extra = row.extra_data or {}
        ingestion = row.ingestion_metadata or {}
        published = extra.get("published_date")
        published_date = date.fromisoformat(published) if isinstance(published, str) else None
        value = row.value_numeric
        price = int(value) if isinstance(value, Decimal) else int(value or 0)
        return EwuraFuelObservationRead(
            id=row.id,
            source_id=row.source_id,
            source_label=row.source.name if row.source is not None else "EWURA",
            scraper_run_id=row.scraper_run_id,
            document_url=str(extra.get("document_url", "")),
            content_sha256=str(ingestion.get("content_sha256", "")),
            published_date=published_date,
            location_id=row.location_id,
            canonical_location_name=row.location.name if row.location is not None else None,
            raw_location_text=str(extra.get("raw_location_text", "")),
            fuel_type=row.energy_detail.fuel_grade if row.energy_detail is not None else "",
            price=price,
            unit=row.unit_override or row.metric.unit or "TZS/Litre",
            recorded_at=row.recorded_at.date(),
            created_at=row.created_at,
        )
