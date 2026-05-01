"""Node 7: Render resume as LaTeX PDF and check page count."""
from __future__ import annotations

import io
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_render(state: AgentState) -> dict[str, Any]:
    """Render the opening resume as a PDF and record page count."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.opening_resume.latex_resume.service import (
        render_resume, get_resume_pdf,
    )

    ctx = get_context()
    events = list(state.get("events", []))
    render_count = state.get("render_count", 0) + 1

    try:
        # Render the PDF
        render_result = await render_resume(ctx.conn, ctx.user_id, ctx.opening_id, layout=None)

        # Count pages
        pdf_result = await get_resume_pdf(ctx.conn, ctx.user_id, ctx.opening_id)
        page_count = 0
        if pdf_result:
            pdf_bytes, _ = pdf_result
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)

        return {
            "pdf_page_count": page_count,
            "render_count": render_count,
            "events": events + [{
                "node": "render",
                "status": "completed",
                "message": f"Rendered PDF: {page_count} page(s), "
                           f"size: {render_result.get('pdf_size_bytes', 0)} bytes",
                "data": {"page_count": page_count, "render_count": render_count},
            }],
        }
    except Exception as e:
        return {
            "pdf_page_count": 0,
            "render_count": render_count,
            "error": f"Render failed: {e}",
            "events": events + [{
                "node": "render",
                "status": "error",
                "message": str(e),
            }],
        }
