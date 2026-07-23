from typing import Any

from pydantic import BaseModel, Field


class BaseResponse[DataT](BaseModel):
    """Optional envelope for consistent API responses."""

    success: bool = True
    data: DataT | None = None
    message: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
