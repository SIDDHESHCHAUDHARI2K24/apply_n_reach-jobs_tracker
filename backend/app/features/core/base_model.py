"""Shared Pydantic base schemas for API models.

These classes provide common configuration and timestamp fields that
can be reused across feature-specific request and response models.
"""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator


class BaseSchema(BaseModel):
    """Base schema configured for ORM-style objects (`from_attributes=True`)."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(BaseSchema):
    """Schema mixin that adds optional creation and update timestamps."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


T = TypeVar("T")


class PaginationParams(BaseSchema):
    """Query params for paginated list endpoints."""

    limit: int = 20
    offset: int = 0

    @field_validator("limit", mode="before")
    @classmethod
    def validate_limit(cls, v):
        v = int(v)
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v

    @field_validator("offset", mode="before")
    @classmethod
    def validate_offset(cls, v):
        v = int(v)
        if v < 0:
            raise ValueError("offset must be >= 0")
        return v


class PaginatedResponse(BaseSchema, Generic[T]):
    """Wrapper for paginated list responses."""

    items: list[T]
    total: int
    limit: int
    offset: int

