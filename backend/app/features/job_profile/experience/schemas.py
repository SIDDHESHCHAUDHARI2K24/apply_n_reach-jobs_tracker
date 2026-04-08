"""Pydantic schemas for the job_profile experience sub-feature."""
import re
from datetime import datetime
from typing import Optional

from pydantic import field_validator, model_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text

_MONTH_YEAR_RE = re.compile(r"^(0[1-9]|1[0-2])\/\d{4}$")


def _parse_month_year(s: str) -> tuple[int, int]:
    """Parse MM/YYYY string into (year, month) tuple for comparison."""
    month, year = s.split("/")
    return int(year), int(month)


class JPExperienceCreate(BaseSchema):
    """Request schema for creating a job profile experience entry."""

    role_title: str
    company_name: str
    start_month_year: str
    end_month_year: Optional[str] = None
    context: str = ""
    work_sample_links: list[str] = []
    bullet_points: list[str] = []

    @field_validator("role_title", mode="before")
    @classmethod
    def sanitize_role_title(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("company_name", mode="before")
    @classmethod
    def sanitize_company_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("start_month_year", mode="before")
    @classmethod
    def validate_start(cls, v):
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("start_month_year must be MM/YYYY format")
        return v

    @field_validator("end_month_year", mode="before")
    @classmethod
    def validate_end(cls, v):
        if v is None:
            return v
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("end_month_year must be MM/YYYY format")
        return v

    @field_validator("context", mode="before")
    @classmethod
    def sanitize_context(cls, v):
        return sanitize_text(v, max_length=10000)

    @field_validator("work_sample_links", mode="before")
    @classmethod
    def sanitize_work_sample_links(cls, v):
        if not isinstance(v, list):
            raise ValueError("work_sample_links must be a list")
        return [sanitize_text(str(item), max_length=2048) for item in v]

    @field_validator("bullet_points", mode="before")
    @classmethod
    def sanitize_bullets(cls, v):
        if not isinstance(v, list):
            raise ValueError("bullet_points must be a list")
        return [sanitize_text(item, max_length=500) for item in v]

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.end_month_year:
            start = _parse_month_year(self.start_month_year)
            end = _parse_month_year(self.end_month_year)
            if end < start:
                raise ValueError("end_month_year must be >= start_month_year")
        return self


class JPExperienceUpdate(BaseSchema):
    """Request schema for partially updating a job profile experience entry (all fields optional)."""

    role_title: Optional[str] = None
    company_name: Optional[str] = None
    start_month_year: Optional[str] = None
    end_month_year: Optional[str] = None
    context: Optional[str] = None
    work_sample_links: Optional[list[str]] = None
    bullet_points: Optional[list[str]] = None

    @field_validator("role_title", mode="before")
    @classmethod
    def sanitize_role_title(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("company_name", mode="before")
    @classmethod
    def sanitize_company_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("start_month_year", mode="before")
    @classmethod
    def validate_start(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("start_month_year must be MM/YYYY format")
        return v

    @field_validator("end_month_year", mode="before")
    @classmethod
    def validate_end(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("end_month_year must be MM/YYYY format")
        return v

    @field_validator("context", mode="before")
    @classmethod
    def sanitize_context(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=10000)

    @field_validator("work_sample_links", mode="before")
    @classmethod
    def sanitize_work_sample_links(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("work_sample_links must be a list")
        return [sanitize_text(str(item), max_length=2048) for item in v]

    @field_validator("bullet_points", mode="before")
    @classmethod
    def sanitize_bullets(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("bullet_points must be a list")
        return [sanitize_text(item, max_length=500) for item in v]

    @model_validator(mode="after")
    def validate_date_order(self):
        # Only validate when BOTH dates are provided in this update
        if self.start_month_year and self.end_month_year:
            start = _parse_month_year(self.start_month_year)
            end = _parse_month_year(self.end_month_year)
            if end < start:
                raise ValueError("end_month_year must be >= start_month_year")
        return self


class JPExperienceResponse(BaseSchema):
    """Response schema for a job profile experience entry."""

    id: int
    job_profile_id: int
    source_experience_id: Optional[int] = None
    role_title: str
    company_name: str
    start_month_year: str
    end_month_year: Optional[str] = None
    context: str
    work_sample_links: list[str] = []
    bullet_points: list[str] = []
    created_at: datetime
    updated_at: datetime
