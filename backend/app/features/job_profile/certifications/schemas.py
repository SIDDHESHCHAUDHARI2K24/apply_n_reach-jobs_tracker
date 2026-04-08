"""Pydantic schemas for the job_profile certifications sub-feature."""
from datetime import datetime
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class JPCertificationCreate(BaseSchema):
    """Request schema for creating a job profile certification entry."""

    certification_name: str
    verification_link: str

    @field_validator("certification_name", mode="before")
    @classmethod
    def sanitize_certification_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("verification_link", mode="before")
    @classmethod
    def sanitize_verification_link(cls, v):
        return sanitize_text(v, max_length=2048)


class JPCertificationUpdate(BaseSchema):
    """Request schema for partially updating a job profile certification entry."""

    certification_name: Optional[str] = None
    verification_link: Optional[str] = None

    @field_validator("certification_name", mode="before")
    @classmethod
    def sanitize_certification_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("verification_link", mode="before")
    @classmethod
    def sanitize_verification_link(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)


class JPCertificationResponse(BaseSchema):
    """Response schema for a job profile certification entry."""

    id: int
    job_profile_id: int
    source_certification_id: Optional[int] = None
    certification_name: str
    verification_link: str
    created_at: datetime
    updated_at: datetime
