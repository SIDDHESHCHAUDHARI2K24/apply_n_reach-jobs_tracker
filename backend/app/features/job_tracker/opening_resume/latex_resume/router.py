"""Router for opening resume LaTeX rendering endpoints."""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.features.auth.utils import get_current_user
from app.features.core.dependencies import DbDep
from app.features.job_tracker.opening_resume.latex_resume import service
from app.features.job_tracker.opening_resume.latex_resume.schemas import (
    RenderedOpeningResumeResponse,
    RenderResumeRequest,
)

router = APIRouter(tags=["job-opening-resume"])


@router.post(
    "/job-openings/{opening_id}/resume/latex-resume/render",
    response_model=RenderedOpeningResumeResponse,
)
async def render_latex_resume(
    opening_id: int,
    data: RenderResumeRequest | None = None,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> RenderedOpeningResumeResponse:
    """Render and store opening resume LaTeX/PDF output."""
    layout = data.layout if data else None
    row = await service.render_resume(conn, current_user["id"], opening_id, layout)
    return RenderedOpeningResumeResponse(**row)


@router.get(
    "/job-openings/{opening_id}/resume/latex-resume",
    response_model=RenderedOpeningResumeResponse,
)
async def get_latex_resume_metadata(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> RenderedOpeningResumeResponse:
    """Get metadata for the latest opening resume render."""
    row = await service.get_latex_resume_metadata(conn, current_user["id"], opening_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rendered resume found for this opening",
        )
    return RenderedOpeningResumeResponse(**row)


@router.get("/job-openings/{opening_id}/resume/latex-resume/pdf")
async def download_latex_resume_pdf(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    """Download rendered PDF for an opening resume."""
    result = await service.get_resume_pdf(conn, current_user["id"], opening_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rendered resume found for this opening",
        )

    pdf_bytes, filename_stem = result
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename_stem}.pdf"'},
    )

