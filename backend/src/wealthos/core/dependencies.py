"""Shared FastAPI dependencies.

Domain modules should import from here (or define local deps that compose these).
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.core.settings import Settings, get_settings


def get_settings_dep() -> Settings:
    return get_settings()


# Re-export for `Depends(get_db)` convenience.
__all__ = ["get_db", "get_settings_dep", "Settings", "Session", "Generator"]
