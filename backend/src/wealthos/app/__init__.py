"""FastAPI application composition (factory, lifespan, root router)."""

from wealthos.app.application import create_application

__all__ = ["create_application"]
