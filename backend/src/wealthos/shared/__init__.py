"""Shared, non-domain helpers (pagination, shared schemas, events, bases).

Keep this thin — business rules belong in modules, not here.
"""

from wealthos.shared.base import (
    BaseMapper,
    BaseRepository,
    BaseResponse,
    BaseService,
)

__all__ = [
    "BaseMapper",
    "BaseRepository",
    "BaseResponse",
    "BaseService",
]
