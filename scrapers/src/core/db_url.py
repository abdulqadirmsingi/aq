"""Normalize database URLs for synchronous SQLAlchemy (Celery workers)."""


def sync_database_url(url: str) -> str:
    """
    Map async SQLAlchemy URLs to a sync driver usable with ``create_engine``.

    Backend defaults use ``postgresql+asyncpg``; scraper fingerprinting uses psycopg3.
    """
    if "+psycopg" in url:
        return url
    if "+asyncpg" in url:
        return url.replace("postgresql+asyncpg", "postgresql+psycopg", 1)
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url
