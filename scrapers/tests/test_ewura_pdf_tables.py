from __future__ import annotations

from src.domains.energy.ewura.pdf_tables import _extract_tables_from_page


class _FakePage:
    def extract_tables(self, *, table_settings):
        if table_settings == {"vertical_strategy": "lines", "horizontal_strategy": "lines"}:
            return [[["Town", "Petrol", "Diesel"], ["Dar", "100", "200"]]]
        if table_settings == {}:
            return [[["Town", "Petrol", "Diesel"], ["Dar", "100", "200"]]]
        return [[["", "300", "400"], ["Arusha", "500", "600"]]]


def test_extract_tables_from_page_combines_unique_tables_across_strategies() -> None:
    tables = _extract_tables_from_page(_FakePage())

    assert len(tables) == 2
    assert tables[0][0] == ["Town", "Petrol", "Diesel"]
    assert tables[1][0] == ["", "300", "400"]
