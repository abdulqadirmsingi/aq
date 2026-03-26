from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.energy.routers.fuel_router import router as fuel_router
from app.modules.money.routers.money_router import router as money_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="AQ Data Intelligence Hub",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if settings.allowed_origins:
        origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
        if origins:
            application.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(fuel_router, prefix="/api/v1")
    application.include_router(money_router, prefix="/api/v1")

    return application


app = create_app()
