"""Pydantic schemas for import operations."""
from pydantic import field_validator

from app.features.core.base_model import BaseSchema


class ImportRequest(BaseSchema):
    """Request schema for importing source items into a job profile."""

    source_ids: list[int]

    @field_validator("source_ids", mode="before")
    @classmethod
    def validate_source_ids(cls, v):
        if not isinstance(v, list):
            raise ValueError("source_ids must be a list")
        if len(v) == 0:
            raise ValueError("source_ids must not be empty")
        if len(v) > 50:
            raise ValueError("Maximum 50 source_ids per import request")
        if len(set(v)) != len(v):
            raise ValueError("source_ids must not contain duplicates")
        if any(not isinstance(i, int) or i <= 0 for i in v):
            raise ValueError("All source_ids must be positive integers")
        return v


class PersonalImportRequest(BaseSchema):
    """Empty body for personal details import (1:1 relationship)."""

    pass


class ImportResult(BaseSchema):
    """Response schema for import operations."""

    imported: list[int]
    skipped: list[int]
    not_found: list[int]
