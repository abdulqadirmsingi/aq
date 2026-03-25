"""Filter listing links to EWURA petroleum cap-price documents only."""

from __future__ import annotations

from urllib.parse import urlparse

from src.domains.energy.ewura.models import DocumentLink, FilteredDocumentRef

_CAP_PRICE_PATH_PREFIX = "/uploads/documents/"

# Match link text or URL (lowercased haystack)
_KEYWORD_FRAGMENTS: tuple[str, ...] = (
    "petroleum",
    "petrolem",  # typo on EWURA site
    "cap price",
    "cap prices",
    "fuel price",
    "fuel prices",
    "bei kikomo",
    "petrol",
    "diesel",
    "kerosene",
    "dizeli",
    "petroli",
    "mafuta",
    "indicative",  # historical "Indicative and Cap" bulletins
    "wholesale",
    "retail cap",
)

_EXCLUDE_SUBSTRINGS: tuple[str, ...] = (
    "price-setting-rules",
    "petroleum-products-price-setting-rules",
    "gn 57",
    "/wp-content/",  # regulations PDFs, not monthly cap tables
)


def filter_documents(links: list[DocumentLink]) -> list[FilteredDocumentRef]:
    """
    Keep only cap-price bulletins under EWURA ``/uploads/documents/``.

    Uses keyword heuristics so minor title/filename changes still match.
    """
    result: list[FilteredDocumentRef] = []
    for link in links:
        if not _passes_filters(link):
            continue
        result.append(FilteredDocumentRef(url=link.url, link_text=link.link_text))
    return result


def _passes_filters(link: DocumentLink) -> bool:
    parsed = urlparse(str(link.url))
    path_lower = parsed.path.lower()
    if not path_lower.startswith(_CAP_PRICE_PATH_PREFIX):
        return False

    haystack = f"{path_lower} {link.link_text.lower()}"
    if any(excl in haystack for excl in _EXCLUDE_SUBSTRINGS):
        return False

    # Hyphenated filenames (e.g. ``bei-kikomo``) should match spaced keywords.
    normalized = haystack.replace("-", " ").replace("_", " ")
    return any(k in normalized for k in _KEYWORD_FRAGMENTS)
