"""Explicit module and platform router registration."""

from __future__ import annotations

from importlib import import_module

from fastapi import FastAPI

from wealthos.modules import MODULES
from wealthos.modules.accounts.api.router import router as accounts_router
from wealthos.modules.categories.api.router import router as categories_router
from wealthos.modules.identity.api.auth_router import router as auth_router
from wealthos.modules.identity.api.me_router import router as me_router
from wealthos.modules.transactions.api.router import router as transactions_router

API_V1_PREFIX = "/api/v1"


def register_modules(app: FastAPI) -> None:
    """Mount auth, me, nested org resources, and domain module routers under /api/v1."""
    app.include_router(auth_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Auth"])
    app.include_router(me_router, prefix=f"{API_V1_PREFIX}/me", tags=["Me"])
    app.include_router(
        accounts_router,
        prefix=f"{API_V1_PREFIX}/organizations",
        tags=["Accounts"],
    )
    app.include_router(
        categories_router,
        prefix=f"{API_V1_PREFIX}/organizations",
        tags=["Categories"],
    )
    app.include_router(
        transactions_router,
        prefix=f"{API_V1_PREFIX}/organizations",
        tags=["Transactions"],
    )

    for module_name in MODULES:
        module = import_module(f"wealthos.modules.{module_name}.api.router")
        app.include_router(
            module.router,
            prefix=f"{API_V1_PREFIX}/{module_name}",
            tags=[module_name.replace("_", " ").title()],
        )
