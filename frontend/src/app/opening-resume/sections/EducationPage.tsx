import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useOREducation } from '@features/opening-resume/sections/useOREducation'

export default function OREducationPage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { items, isLoading, isSaving, error, create, remove } = useOREducation(openingId ?? '')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ institution: '', degree: '' })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div role="alert">{error}</div>

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!form.institution.trim() || !form.degree.trim()) return
    try {
      await create({ institution: form.institution.trim(), degree: form.degree.trim(), field_of_study: null, start_date: null, end_date: null, gpa: null, bullet_points: [] })
      setForm({ institution: '', degree: '' })
      setShowForm(false)
    } catch { /* error shown by hook */ }
  }

  return (
    <div>
      <h3>Education (Snapshot)</h3>
      <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Independent snapshot — changes here do not affect your source profile.</p>

      {items.length === 0 && !showForm && <p>No education entries yet.</p>}

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {items.map(item => (
          <li key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', borderBottom: '1px solid #e5e7eb' }}>
            <span>{item.institution} — {item.degree}</span>
            <button onClick={() => remove(item.id).catch(() => {})} disabled={isSaving}>Delete</button>
          </li>
        ))}
      </ul>

      {showForm && (
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
          <input required placeholder="Institution" value={form.institution} onChange={e => setForm(f => ({ ...f, institution: e.target.value }))} />
          <input required placeholder="Degree" value={form.degree} onChange={e => setForm(f => ({ ...f, degree: e.target.value }))} />
          <button type="submit" disabled={isSaving}>Save</button>
          <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
        </form>
      )}

      <button onClick={() => setShowForm(s => !s)} style={{ marginTop: '0.5rem' }}>+ Add Education</button>
    </div>
  )
}
