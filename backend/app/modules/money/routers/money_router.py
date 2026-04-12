"""Aggregate money routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.money.routers.exchange_rate_router import (
    router as exchange_rate_router,
)
from app.modules.money.routers.stock_router import router as stock_router

router = APIRouter(prefix="/money", tags=["money"])
router.include_router(exchange_rate_router)
router.include_router(stock_router)
