"""Pydantic schemas for the job_tracker openings_core sub-feature."""
from enum import Enum
from typing import Any

from pydantic import field_validator

from app.features.core.base_model import BaseSchema, TimestampedSchema
from app.features.user_profile.validators import sanitize_text
from app.features.job_tracker.validators import validate_url


class OpeningStatus(str, Enum):
    Interested = "Interested"
    Applied = "Applied"
    Interviewing = "Interviewing"
    Offer = "Offer"
    Withdrawn = "Withdrawn"
    Rejected = "Rejected"


class OpeningCreate(BaseSchema):
    source_url: str | None = None
    company_name: str
    role_name: str
    notes: str | None = None
    initial_status: OpeningStatus = OpeningStatus.Interested

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_source_url(cls, v):
        return validate_url(v)

    @field_validator("company_name", mode="before")
    @classmethod
    def validate_company_name(cls, v):
        result = sanitize_text(v)
        if not result:
            raise ValueError("company_name must not be empty")
        return result

    @field_validator("role_name", mode="before")
    @classmethod
    def validate_role_name(cls, v):
        result = sanitize_text(v)
        if not result:
            raise ValueError("role_name must not be empty")
        return result

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v):
        return sanitize_text(v)


class OpeningUpdate(BaseSchema):
    source_url: str | None = None
    company_name: str | None = None
    role_name: str | None = None
    notes: str | None = None

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_source_url(cls, v):
        return validate_url(v)

    @field_validator("company_name", mode="before")
    @classmethod
    def validate_company_name(cls, v):
        if v is None:
            return v
        result = sanitize_text(v)
        if not result:
            raise ValueError("company_name must not be empty")
        return result

    @field_validator("role_name", mode="before")
    @classmethod
    def validate_role_name(cls, v):
        if v is None:
            return v
        result = sanitize_text(v)
        if not result:
            raise ValueError("role_name must not be empty")
        return result

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v):
        return sanitize_text(v)


class OpeningResponse(TimestampedSchema):
    id: int
    user_id: int
    job_profile_id: int | None
    source_url: str | None
    company_name: str
    role_name: str
    current_status: OpeningStatus
    notes: str | None


class OpeningListParams(BaseSchema):
    status: OpeningStatus | None = None
    company_name: str | None = None
    role_name: str | None = None
    limit: int = 20
    after_id: int | None = None


class OpeningListResponse(BaseSchema):
    items: list[OpeningResponse]
    has_more: bool
    next_cursor: int | None


class StatusTransitionRequest(BaseSchema):
    status: OpeningStatus


class StatusHistoryEntry(BaseSchema):
    id: int
    opening_id: int
    from_status: OpeningStatus | None
    to_status: OpeningStatus
    changed_at: Any
    changed_by_user_id: int
