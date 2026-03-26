"""Aggregate EWURA fuel routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.energy.routers.fuel_data_router import router as fuel_data_router
from app.modules.energy.routers.fuel_monitor_router import (
    router as fuel_monitor_router,
)

router = APIRouter(prefix="/energy", tags=["energy"])
router.include_router(fuel_data_router)
router.include_router(fuel_monitor_router)
