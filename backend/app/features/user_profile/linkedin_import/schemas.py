"""Schemas for LinkedIn profile import."""
from __future__ import annotations
from app.features.core.base_model import BaseSchema
from pydantic import Field


class LinkedInImportRequest(BaseSchema):
    """Request to import a LinkedIn profile."""
    linkedin_url: str = Field(description="LinkedIn profile URL to import")


class LinkedInImportResponse(BaseSchema):
    """Response after LinkedIn import completes."""
    message: str
    sections_imported: dict[str, int] = Field(
        description="Count of entries imported per section"
    )


class MappedPersonal(BaseSchema):
    full_name: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None


class MappedEducation(BaseSchema):
    university_name: str
    major: str = ""
    degree_type: str = ""
    start_month_year: str = ""
    end_month_year: str | None = None
    bullet_points: list[str] = []
    reference_links: list[str] = []


class MappedExperience(BaseSchema):
    role_title: str
    company_name: str
    start_month_year: str = ""
    end_month_year: str | None = None
    context: str = ""
    work_sample_links: list[str] = []
    bullet_points: list[str] = []


class MappedProject(BaseSchema):
    project_name: str
    description: str = ""
    start_month_year: str = ""
    end_month_year: str | None = None
    reference_links: list[str] = []


class MappedCertification(BaseSchema):
    certification_name: str
    verification_link: str | None = None


class MappedSkill(BaseSchema):
    kind: str = "technical"
    name: str
    sort_order: int = 0


class MappedLinkedInProfile(BaseSchema):
    """Complete mapped LinkedIn profile."""
    personal: MappedPersonal | None = None
    educations: list[MappedEducation] = []
    experiences: list[MappedExperience] = []
    projects: list[MappedProject] = []
    certifications: list[MappedCertification] = []
    skills: list[MappedSkill] = []
