"""Pydantic schemas for job_opening_certifications."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class CertificationResponse(BaseSchema):
    """Response schema for a job opening resume certification entry."""

    id: int
    resume_id: int
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    display_order: int = 0


class CertificationCreate(BaseSchema):
    """Request schema for creating a job opening certification entry."""

    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    display_order: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("issuer", "credential_id", mode="before")
    @classmethod
    def sanitize_short_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("issue_date", "expiry_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)


class CertificationUpdate(BaseSchema):
    """Request schema for partial update of a job opening certification entry."""

    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    display_order: Optional[int] = None

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("issuer", "credential_id", mode="before")
    @classmethod
    def sanitize_short_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("issue_date", "expiry_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)
