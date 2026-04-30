"""Pydantic schemas for job_profile core."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema, PaginationParams
from app.features.user_profile.validators import sanitize_text


class JobProfileCreate(BaseSchema):
    """Request schema for creating a job profile."""

    profile_name: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    job_posting_url: Optional[str] = None

    @field_validator("profile_name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("target_role", mode="before")
    @classmethod
    def sanitize_role(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("target_company", mode="before")
    @classmethod
    def sanitize_company(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("job_posting_url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)


class JobProfileUpdate(BaseSchema):
    """Request schema for partially updating a job profile (all fields optional)."""

    profile_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    job_posting_url: Optional[str] = None
    status: Optional[Literal["draft", "active", "archived"]] = None

    @field_validator("profile_name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("target_role", mode="before")
    @classmethod
    def sanitize_role(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("target_company", mode="before")
    @classmethod
    def sanitize_company(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("job_posting_url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)


class JobProfileResponse(BaseSchema):
    """Response schema for a job profile."""

    id: int
    user_id: int
    profile_name: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    job_posting_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class JobProfileListParams(PaginationParams):
    """Query params for listing job profiles with optional status filter."""

    status: Optional[Literal["draft", "active", "archived"]] = None
