from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageMeta(BaseModel):
    limit: int
    offset: int
    total: int
    has_next: bool


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


def build_page(items: Sequence[T], *, total: int, limit: int, offset: int) -> Page[T]:
    return Page[T](
        items=list(items),
        meta=PageMeta(
            limit=limit,
            offset=offset,
            total=total,
            has_next=offset + len(items) < total,
        ),
    )
