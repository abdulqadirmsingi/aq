"""Extract table grids from DOCX bytes (in-memory)."""

from __future__ import annotations

from io import BytesIO

from docx import Document


def extract_tables_from_docx(
    docx_bytes: bytes,
) -> tuple[list[list[list[str | None]]], str]:
    """
    Return all document tables plus paragraph text (for effective dates).

    Tables match the PDF shape: ``list[row][col]`` with ``None`` for empty cells.
    """
    doc = Document(BytesIO(docx_bytes))
    header_lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    header_text = "\n".join(header_lines[:50])[:8000]

    tables: list[list[list[str | None]]] = []
    for table in doc.tables:
        rows: list[list[str | None]] = []
        for row in table.rows:
            cells: list[str | None] = []
            for cell in row.cells:
                t = cell.text.replace("\n", " ").strip()
                cells.append(t if t else None)
            rows.append(cells)
        if rows:
            tables.append(rows)
    return tables, header_text
