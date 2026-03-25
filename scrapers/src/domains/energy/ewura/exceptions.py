"""EWURA scraper-specific errors."""


class EwuraScraperError(Exception):
    """Base class for recoverable EWURA pipeline errors."""


class EwuraDownloadTooLargeError(EwuraScraperError):
    """Response body exceeds configured in-memory cap."""


class EwuraUnsupportedDocumentError(EwuraScraperError):
    """Format not handled in this phase (e.g. DOCX before Phase 3)."""
