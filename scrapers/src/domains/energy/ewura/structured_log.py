"""Stable ``extra=`` keys for EWURA pipeline logs (JSON-friendly in aggregators)."""

from __future__ import annotations

import logging
from typing import Any


def ewura_extra(
    *,
    event: str,
    document_url: str | None = None,
    **fields: Any,
) -> dict[str, Any]:
    """Build a logging ``extra`` dict; always includes ``ewura_event``."""
    out: dict[str, Any] = {"ewura_event": event}
    if document_url is not None:
        out["document_url"] = document_url
    for key, value in fields.items():
        if value is not None:
            out[key] = value
    return out


def ewura_info(
    logger: logging.Logger,
    msg: str,
    *,
    event: str,
    document_url: str | None = None,
    **fields: Any,
) -> None:
    extra = ewura_extra(event=event, document_url=document_url, **fields)
    logger.info(msg, extra=extra)


def ewura_warning(
    logger: logging.Logger,
    msg: str,
    *,
    event: str,
    document_url: str | None = None,
    **fields: Any,
) -> None:
    extra = ewura_extra(event=event, document_url=document_url, **fields)
    logger.warning(msg, extra=extra)


def ewura_error(
    logger: logging.Logger,
    msg: str,
    *,
    event: str,
    document_url: str | None = None,
    **fields: Any,
) -> None:
    extra = ewura_extra(event=event, document_url=document_url, **fields)
    logger.error(msg, extra=extra)
