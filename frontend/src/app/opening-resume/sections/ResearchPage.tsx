import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useORResearch } from '@features/opening-resume/sections/useORResearch'

export default function ORResearchPage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { items, isLoading, isSaving, error, create, remove } = useORResearch(openingId ?? '')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '' })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div role="alert">{error}</div>

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!form.title.trim()) return
    try {
      await create({ title: form.title.trim(), institution: null, journal: null, year: null, description: null, url: null, bullet_points: [], reference_links: [] })
      setForm({ title: '' })
      setShowForm(false)
    } catch { /* error shown by hook */ }
  }

  return (
    <div>
      <h3>Research (Snapshot)</h3>
      <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Independent snapshot — changes here do not affect your source profile.</p>

      {items.length === 0 && !showForm && <p>No research entries yet.</p>}

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {items.map(item => (
          <li key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', borderBottom: '1px solid #e5e7eb' }}>
            <span>{item.title}</span>
            <button onClick={() => remove(item.id).catch(() => {})} disabled={isSaving}>Delete</button>
          </li>
        ))}
      </ul>

      {showForm && (
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
          <input required placeholder="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          <button type="submit" disabled={isSaving}>Save</button>
          <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
        </form>
      )}

      <button onClick={() => setShowForm(s => !s)} style={{ marginTop: '0.5rem' }}>+ Add Research</button>
    </div>
  )
}
