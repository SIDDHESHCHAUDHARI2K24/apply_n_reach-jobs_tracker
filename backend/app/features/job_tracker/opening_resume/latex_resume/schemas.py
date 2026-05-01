"""Pydantic schemas for opening resume LaTeX rendering."""

from datetime import datetime

from app.features.core.base_model import BaseSchema
from app.features.job_profile.latex_resume.schemas import ResumeLayoutOptions


class RenderResumeRequest(BaseSchema):
    """Optional render parameters."""

    layout: ResumeLayoutOptions | None = None


class RenderedOpeningResumeResponse(BaseSchema):
    """Metadata for the latest opening resume render."""

    resume_id: int
    template_name: str
    updated_at: datetime
    latex_length: int
    pdf_size_bytes: int

