"""Explicit module router registration.

Keeps application.py free of a growing list of include_router calls.
"""

from __future__ import annotations

from importlib import import_module

from fastapi import FastAPI

from wealthos.modules import MODULES


def register_modules(app: FastAPI) -> None:
    """Import each module router and mount it under /{module_name}."""
    for module_name in MODULES:
        module = import_module(f"wealthos.modules.{module_name}.api.router")
        router = module.router
        app.include_router(
            router,
            prefix=f"/{module_name}",
            tags=[module_name.replace("_", " ").title()],
        )
