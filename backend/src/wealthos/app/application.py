from fastapi import FastAPI

from wealthos.app.lifespan import lifespan
from wealthos.app.router import router
from wealthos.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app
