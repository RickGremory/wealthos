"""Shared building blocks reused by every domain module."""

from wealthos.shared.base.base_mapper import BaseMapper
from wealthos.shared.base.base_repository import BaseRepository
from wealthos.shared.base.base_response import BaseResponse
from wealthos.shared.base.base_service import BaseService

__all__ = [
    "BaseMapper",
    "BaseRepository",
    "BaseResponse",
    "BaseService",
]
