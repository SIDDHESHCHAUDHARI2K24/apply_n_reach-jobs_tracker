"""
ui/backend/main.py
-------------------
FastAPI backend for the Outreach Email UI (T4).

Exposes REST endpoints that the React frontend calls.
Bridges HTTP requests to the LangGraph graph.

Endpoints:
  POST /api/generate     — run graph (invocation 1, up to HITL interrupt)
  POST /api/resume       — resume graph after user review (invocation 2)
  GET  /api/status/{id}  — get current snapshot for a thread
  GET  /api/health       — health check

Run locally:
    cd ui/backend
    uvicorn main:app --reload --port 8000

CORS is configured to allow the React dev server on localhost:5173.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from the project root (state.py, graph.py, nodes/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from typing import Optional
import uuid
import os
import io

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import resend

from graph import graph
from state import initial_state

# Resend configuration — reads from .env
resend.api_key = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")

app = FastAPI(title="Outreach Email API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite React dev server
        "http://localhost:3000",   # CRA fallback
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory snapshot store — maps thread_id → last graph result
_snapshots: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    job_description: str
    resume: str
    recipient_type: str             # recruiter | team_member | hiring_manager
    linkedin_paste: Optional[str] = None
    thread_id: Optional[str] = None  # auto-generated if not provided


class ResumeRequest(BaseModel):
    thread_id: str
    edited_body: str
    selected_subject: str
    reset_to_ai: bool = False


class GenerateResponse(BaseModel):
    thread_id: str
    recipient_type: str
    email_body: str
    word_count: int
    subject_options: list[str]
    followup_body: str
    followup_days: int
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_title: Optional[str]
    apollo_found: bool
    personalization_signals: list[str]
    warnings: list[str]


class ResumeResponse(BaseModel):
    thread_id: str
    status: str
    email_body: str
    selected_subject: str
    word_count: int
    contact_email: Optional[str]


class SendRequest(BaseModel):
    thread_id: str
    to_email: str
    subject: str
    body: str
    sender_name: Optional[str] = "AI Outreach Assistant"


class SendResponse(BaseModel):
    success: bool
    message: str
    resend_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract plain text from an uploaded PDF, DOCX, or TXT file.
    Returns the extracted text as a JSON string.

    Supported types:
      .pdf  — via pypdf
      .docx — via python-docx
      .txt  — plain read
    """
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    allowed = {"pdf", "docx", "txt"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(allowed))}"
        )

    contents = await file.read()

    try:
        if ext == "txt":
            text = contents.decode("utf-8", errors="replace")

        elif ext == "pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                raise HTTPException(
                    status_code=503,
                    detail="PDF support requires pypdf. Run: pip install pypdf"
                )
            reader = PdfReader(io.BytesIO(contents))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages).strip()

        elif ext == "docx":
            try:
                import docx
            except ImportError:
                raise HTTPException(
                    status_code=503,
                    detail="DOCX support requires python-docx. Run: pip install python-docx"
                )
            doc = docx.Document(io.BytesIO(contents))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs).strip()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from {filename}: {exc}"
        )

    if not text:
        raise HTTPException(
            status_code=422,
            detail=f"No text could be extracted from {filename}. The file may be scanned or image-based."
        )

    return {"filename": filename, "text": text, "char_count": len(text)}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """
    Run the outreach graph from start up to the HITL interrupt.
    Returns the generated email, subject lines, follow-up draft,
    and any contact info found by Apollo.
    """
    valid_types = {"recruiter", "team_member", "hiring_manager"}
    if req.recipient_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"recipient_type must be one of: {', '.join(sorted(valid_types))}"
        )

    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = initial_state(
        raw_jd=req.job_description,
        raw_resume=req.resume,
        recipient_type=req.recipient_type,
    )
    if req.linkedin_paste and req.linkedin_paste.strip():
        state["raw_linkedin_paste"] = req.linkedin_paste  # type: ignore

    try:
        result = graph.invoke(state, config=config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Graph error: {exc}")

    _snapshots[thread_id] = result

    emails = result.get("generated_emails") or []
    subject_sets = result.get("subject_lines") or []
    followups = result.get("followup_drafts") or []
    apollo = result.get("apollo_result") or {}

    email_body = emails[0]["body"] if emails else ""
    word_count = emails[0]["word_count"] if emails else 0
    signals = emails[0].get("personalization_signals", []) if emails else []
    subject_options = subject_sets[0].get("options", []) if subject_sets else []
    followup_body = followups[0].get("body", "") if followups else ""
    followup_days = followups[0].get("suggested_send_after_days", 7) if followups else 7

    return GenerateResponse(
        thread_id=thread_id,
        recipient_type=req.recipient_type,
        email_body=email_body,
        word_count=word_count,
        subject_options=subject_options,
        followup_body=followup_body,
        followup_days=followup_days,
        contact_name=result.get("contact_name"),
        contact_email=result.get("verified_email"),
        contact_title=result.get("contact_title"),
        apollo_found=bool(apollo.get("found")),
        personalization_signals=signals,
        warnings=result.get("errors") or [],
    )


@app.post("/api/resume", response_model=ResumeResponse)
def resume(req: ResumeRequest):
    """
    Resume the graph after the user has reviewed and optionally edited
    the generated email. Triggers export_node and finalizes the package.
    """
    if req.thread_id not in _snapshots:
        raise HTTPException(
            status_code=404,
            detail=f"No active session for thread_id '{req.thread_id}'. Run /api/generate first."
        )

    snapshot = _snapshots[req.thread_id]
    recipient_type = snapshot.get("recipient_type", "recruiter")
    config = {"configurable": {"thread_id": req.thread_id}}

    user_edits = [{
        "recipient_type": recipient_type,
        "edited_body": req.edited_body,
        "edited_subject": req.selected_subject,
        "reset_to_ai": req.reset_to_ai,
    }]

    try:
        final = graph.invoke({"user_edits": user_edits}, config=config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Graph resume error: {exc}")

    _snapshots[req.thread_id] = final

    emails = final.get("generated_emails") or []
    email_body = emails[0]["body"] if emails else req.edited_body
    word_count = emails[0]["word_count"] if emails else len(req.edited_body.split())

    return ResumeResponse(
        thread_id=req.thread_id,
        status=final.get("outreach_status", "drafted"),
        email_body=email_body,
        selected_subject=req.selected_subject,
        word_count=word_count,
        contact_email=final.get("verified_email"),
    )


@app.post("/api/send", response_model=SendResponse)
def send_email(req: SendRequest):
    """
    Send the finalized outreach email via Resend.

    Requires RESEND_API_KEY in .env.
    For testing without a verified domain, use RESEND_FROM_EMAIL=onboarding@resend.dev
    and send only to your own email address (Resend sandbox restriction).
    """
    if not resend.api_key:
        raise HTTPException(
            status_code=503,
            detail="RESEND_API_KEY not set. Add it to your .env file."
        )

    if not req.to_email or "@" not in req.to_email:
        raise HTTPException(
            status_code=400,
            detail="Invalid recipient email address."
        )

    try:
        response = resend.Emails.send({
            "from": RESEND_FROM,
            "to": [req.to_email],
            "subject": req.subject,
            "text": req.body,
        })

        # Update snapshot status to "sent"
        if req.thread_id in _snapshots:
            _snapshots[req.thread_id]["outreach_status"] = "sent"

        return SendResponse(
            success=True,
            message=f"Email sent successfully to {req.to_email}",
            resend_id=response.get("id"),
        )

    except Exception as exc:
        return SendResponse(
            success=False,
            message=f"Failed to send: {str(exc)}",
        )


@app.get("/api/status/{thread_id}")
def get_status(thread_id: str):
    """Return the full snapshot for a thread (for debugging or review)."""
    snapshot = _snapshots.get(thread_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Thread not found")

    emails = snapshot.get("generated_emails") or []
    subject_sets = snapshot.get("subject_lines") or []
    followups = snapshot.get("followup_drafts") or []

    return {
        "thread_id": thread_id,
        "outreach_status": snapshot.get("outreach_status"),
        "recipient_type": snapshot.get("recipient_type"),
        "contact_name": snapshot.get("contact_name"),
        "contact_email": snapshot.get("verified_email"),
        "contact_title": snapshot.get("contact_title"),
        "email_body": emails[0]["body"] if emails else None,
        "subject_options": subject_sets[0].get("options", []) if subject_sets else [],
        "followup_body": followups[0].get("body") if followups else None,
        "warnings": snapshot.get("errors") or [],
        "debug_log": snapshot.get("debug_log") or [],
    }
