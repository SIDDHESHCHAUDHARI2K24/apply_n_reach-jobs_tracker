"""Router for job profile latex_resume endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.features.core.dependencies import DbDep
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.latex_resume import service
from app.features.job_profile.latex_resume.schemas import (
    RenderResumeRequest,
    RenderedResumeResponse,
)

router = APIRouter(
    prefix="/job-profiles/{job_profile_id}/latex-resume",
    tags=["latex-resume"],
)


@router.post("/render", response_model=RenderedResumeResponse)
async def render_resume(
    data: RenderResumeRequest | None = None,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> RenderedResumeResponse:
    """Render a LaTeX resume for the job profile. Creates or overwrites the stored render."""
    layout = data.layout if data else None
    row = await service.render_resume(conn, job_profile["id"], layout)
    return RenderedResumeResponse(**row)


@router.get("", response_model=RenderedResumeResponse)
async def get_resume_metadata(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> RenderedResumeResponse:
    """Get metadata for the last rendered resume. 404 if never rendered."""
    row = await service.get_rendered_resume(conn, job_profile["id"])
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rendered resume found for this job profile",
        )
    return RenderedResumeResponse(**row)


@router.get("/pdf")
async def get_resume_pdf(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> Response:
    """Download the rendered PDF. 404 if never rendered."""
    result = await service.get_resume_pdf(conn, job_profile["id"])
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rendered resume found for this job profile",
        )
    pdf_bytes, filename_stem = result
    filename = f"{filename_stem}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
