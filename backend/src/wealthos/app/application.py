from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wealthos.app.lifespan import lifespan
from wealthos.app.router import router
from wealthos.core.config import settings
from wealthos.core.middleware import RequestTimingMiddleware
from wealthos.modules.router_registry import register_modules


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestTimingMiddleware)
    app.include_router(router)
    register_modules(app)
    return app
