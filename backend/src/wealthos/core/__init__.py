"""Cross-cutting runtime: settings, database, logging, security."""

from wealthos.core.config import settings
from wealthos.core.settings import Settings, get_settings

__all__ = ["Settings", "get_settings", "settings"]
