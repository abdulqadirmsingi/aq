from datetime import UTC, date
from decimal import Decimal

from src.domains.money.fx_models import (
    ExchangeRateDetailPayload,
    PersistObservationResult,
)
from src.domains.money.fx_utils import (
    build_external_reference,
    build_recorded_at,
    compute_inverse_rate,
    parse_decimal_number,
    parse_source_timestamp,
    payload_fingerprint,
)


def test_parse_decimal_number_removes_grouping_commas() -> None:
    assert parse_decimal_number("2,535.50") == Decimal("2535.50")


def test_build_external_reference_tracks_update_dimensions() -> None:
    assert (
        build_external_reference(
            instrument_code="usd",
            metric_slug="fx_buy_rate",
            channel="cash",
            cash_note_band="notes_50_500",
            source_effective_date=date(2026, 3, 25),
        )
        == "USD|fx_buy_rate|cash|notes_50_500|2026-03-25"
    )


def test_build_recorded_at_sets_utc_boundary() -> None:
    assert (
        build_recorded_at(date(2026, 3, 25)).isoformat()
        == "2026-03-25T00:00:00+00:00"
    )


def test_parse_source_timestamp_assigns_utc_when_missing_timezone() -> None:
    parsed = parse_source_timestamp("Mar 25, 2026, 22:33")
    assert parsed.tzinfo == UTC
    assert parsed.hour == 22


def test_compute_inverse_rate_returns_none_for_zero() -> None:
    assert compute_inverse_rate(Decimal("0")) is None


def test_payload_fingerprint_is_stable_for_dict_order() -> None:
    detail = ExchangeRateDetailPayload(
        instrument_code="USD",
        rate_kind="buy",
        market_scope="commercial_bank",
    )
    left = payload_fingerprint(
        value=Decimal("2535"),
        unit_override="TZS",
        detail=detail,
        extra_data={"b": 2, "a": 1},
        ingestion_metadata={"z": 9, "x": 7},
    )
    right = payload_fingerprint(
        value=Decimal("2535"),
        unit_override="TZS",
        detail=detail,
        extra_data={"a": 1, "b": 2},
        ingestion_metadata={"x": 7, "z": 9},
    )
    assert left == right


def test_persist_observation_result_adds_counts() -> None:
    left = PersistObservationResult(inserted=1, updated=2, skipped=3)
    right = PersistObservationResult(inserted=4, updated=5, skipped=6)
    assert left + right == PersistObservationResult(inserted=5, updated=7, skipped=9)
