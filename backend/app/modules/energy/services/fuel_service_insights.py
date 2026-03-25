"""Derived EWURA fuel summaries, rollups, and insights."""

from __future__ import annotations

from app.modules.energy.schemas.fuel import (
    EwuraFuelDashboardSummaryRead,
    EwuraFuelInsightRead,
    EwuraFuelLatestExtremesRead,
    EwuraFuelRollupRead,
)


class FuelInsightServiceMixin:
    async def get_rollups(
        self,
        *,
        level: str,
        fuel_type: str | None,
    ) -> list[EwuraFuelRollupRead]:
        latest = await self.get_latest_prices(fuel_type=fuel_type, location_query=None)
        grouped: dict[tuple[str, str], list] = {}
        for item in latest:
            group_name = self._group_name(item, level)
            if group_name is None:
                continue
            grouped.setdefault((group_name, item.fuel_type), []).append(item)

        rollups: list[EwuraFuelRollupRead] = []
        for (group_name, current_fuel_type), items in sorted(grouped.items()):
            prices = [item.price for item in items]
            if not prices:
                continue
            snapshot_date = items[0].snapshot_date
            avg_price = int(sum(prices) / len(prices))
            min_price = min(prices)
            max_price = max(prices)
            rollups.append(
                EwuraFuelRollupRead(
                    snapshot_date=snapshot_date,
                    snapshot_month_label=self._month_label(snapshot_date),
                    level=level,
                    group_name=group_name,
                    fuel_type=current_fuel_type,
                    observations_count=len(items),
                    avg_price=avg_price,
                    avg_price_display=self._price_display(avg_price, items[0].unit),
                    min_price=min_price,
                    min_price_display=self._price_display(min_price, items[0].unit),
                    max_price=max_price,
                    max_price_display=self._price_display(max_price, items[0].unit),
                )
            )
        return rollups

    async def get_latest_extremes(
        self,
        *,
        fuel_type: str | None,
        top: int,
    ) -> EwuraFuelLatestExtremesRead | None:
        latest = await self.get_latest_prices(fuel_type=fuel_type, location_query=None)
        if not latest:
            return None
        sorted_prices = sorted(latest, key=lambda item: (item.price, item.raw_location_text))
        return EwuraFuelLatestExtremesRead(
            snapshot_date=latest[0].snapshot_date,
            snapshot_month_label=latest[0].snapshot_month_label,
            fuel_type=fuel_type,
            cheapest=[self._to_extreme_item(item) for item in sorted_prices[:top]],
            most_expensive=[self._to_extreme_item(item) for item in sorted_prices[-top:][::-1]],
        )

    async def get_insights(self) -> list[EwuraFuelInsightRead]:
        latest_summary = await self.get_latest_summary()
        latest_prices = await self.get_latest_prices(fuel_type=None, location_query=None)
        trends = await self.get_current_year_trends(year=None, fuel_type=None)
        if latest_summary is None or not latest_prices:
            return []

        insights: list[EwuraFuelInsightRead] = []
        for item in latest_summary.items:
            matching_prices = [price for price in latest_prices if price.fuel_type == item.fuel_type]
            changed = [price for price in matching_prices if price.percent_change is not None]
            if changed:
                avg_change = round(
                    sum(price.percent_change for price in changed if price.percent_change is not None)
                    / len(changed),
                    2,
                )
                direction = "increased" if avg_change > 0 else "decreased" if avg_change < 0 else "stayed flat"
                insights.append(
                    EwuraFuelInsightRead(
                        title=f"{item.fuel_type.title()} month-over-month movement",
                        body=(
                            f"In {latest_summary.snapshot_month_label}, average {item.fuel_type} prices "
                            f"{direction} by {abs(avg_change):.2f}% across {item.locations_count} locations."
                        ),
                        fuel_type=item.fuel_type,
                    )
                )

        if trends:
            latest_month = max(trends, key=lambda row: row.month_start)
            latest_month_rows = [row for row in trends if row.month_start == latest_month.month_start]
            if latest_month_rows:
                top_fuel = max(latest_month_rows, key=lambda row: row.avg_price)
                insights.append(
                    EwuraFuelInsightRead(
                        title="Highest average fuel this month",
                        body=(
                            f"{top_fuel.fuel_type.title()} had the highest average price in "
                            f"{top_fuel.month_label} at {top_fuel.avg_price_display}."
                        ),
                        fuel_type=top_fuel.fuel_type,
                    )
                )
        return insights

    async def get_dashboard_summary(self) -> EwuraFuelDashboardSummaryRead:
        latest_summary = await self.get_latest_summary()
        latest_prices = await self.get_latest_prices(fuel_type=None, location_query=None)
        trends = await self.get_current_year_trends(year=None, fuel_type=None)
        available_months = await self.get_available_months()
        insights = await self.get_insights()
        return EwuraFuelDashboardSummaryRead(
            latest_summary=latest_summary,
            latest_prices_preview=latest_prices[:12],
            current_year_trends=trends,
            available_months=available_months,
            insights=insights,
        )
