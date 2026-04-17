import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useORPersonal } from '@features/opening-resume/sections/useORPersonal'

export default function ORPersonalPage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { data, isLoading, isSaving, error, save } = useORPersonal(openingId ?? '')
  const [form, setForm] = useState({ full_name: '', email: '', summary: '' })

  // Sync form with loaded data
  useEffect(() => {
    if (data) {
      setForm({ full_name: data.full_name ?? '', email: data.email ?? '', summary: data.summary ?? '' })
    }
  }, [data])

  if (isLoading) return <div>Loading...</div>
  if (error) return <div role="alert">{error}</div>

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    try {
      await save({ full_name: form.full_name || null, email: form.email || null, summary: form.summary || null })
    } catch { /* error shown by hook */ }
  }

  return (
    <div>
      <h3>Personal Details (Snapshot)</h3>
      <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Editing this snapshot does not affect your main profile.</p>
      <form onSubmit={handleSave}>
        <div><label>Full name: <input value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} /></label></div>
        <div><label>Email: <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} /></label></div>
        <div><label>Summary: <textarea value={form.summary} onChange={e => setForm(f => ({ ...f, summary: e.target.value }))} rows={4} /></label></div>
        <button type="submit" disabled={isSaving} style={{ marginTop: '0.5rem' }}>{isSaving ? 'Saving...' : 'Save'}</button>
      </form>
    </div>
  )
}
