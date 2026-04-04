// src/api.js
// Thin wrapper around fetch calls to the FastAPI backend.

const BASE = '/api'

export async function generateEmail({ jobDescription, resume, recipientType, linkedinPaste }) {
  const res = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_description: jobDescription,
      resume,
      recipient_type: recipientType,
      linkedin_paste: linkedinPaste || null,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function resumeAfterReview({ threadId, editedBody, selectedSubject, resetToAi }) {
  const res = await fetch(`${BASE}/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      thread_id: threadId,
      edited_body: editedBody,
      selected_subject: selectedSubject,
      reset_to_ai: resetToAi || false,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}
