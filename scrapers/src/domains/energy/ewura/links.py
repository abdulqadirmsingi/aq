"""Extract PDF and DOCX links from HTML."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from src.domains.energy.ewura.models import DocumentLink


def extract_document_links(html: str, page_url: str) -> list[DocumentLink]:
    """
    Parse ``a[href]`` targets ending in ``.pdf`` or ``.docx`` (case-insensitive).

    Resolves relative URLs against ``page_url``.
    """
    soup = BeautifulSoup(html, "lxml")
    base = page_url
    out: list[DocumentLink] = []
    seen: set[str] = set()

    for tag in soup.find_all("a", href=True):
        raw_href = str(tag["href"]).strip()
        if not raw_href or raw_href.startswith("#"):
            continue
        path = urlparse(raw_href).path.lower()
        if not (path.endswith(".pdf") or path.endswith(".docx")):
            continue
        absolute = urljoin(base, raw_href)
        normalized = absolute.split("#")[0]
        if normalized in seen:
            continue
        seen.add(normalized)
        text = tag.get_text(" ", strip=True) or ""
        out.append(DocumentLink(url=normalized, link_text=text))

    return out
