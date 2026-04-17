import { useState } from 'react'
import { useResearch } from './useResearch'
import { ResearchForm } from './ResearchForm'
import type { Research } from '@features/user-profile/types'

export function ResearchList() {
  const { items, isLoading, isSaving, error, create, update, remove } = useResearch()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Research | null>(null)

  if (isLoading) return <div>Loading research...</div>

  async function handleCreate(data: Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    try {
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleUpdate(data: Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this research entry?')) return
    try {
      await remove(id)
    } catch {
      // error displayed by hook's error state
    }
  }

  return (
    <div>
      <h2>Research</h2>
      {error && <div role="alert" style={{ color: 'red' }}>{error}</div>}

      {items.map(item => (
        <div key={item.id} style={{ border: '1px solid #e5e7eb', padding: '1rem', marginBottom: '0.5rem', borderRadius: '4px' }}>
          {editing?.id === item.id ? (
            <ResearchForm
              initial={item}
              isSaving={isSaving}
              onSave={handleUpdate}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <>
              <strong>{item.title}</strong>
              {item.journal && <span> — {item.journal}</span>}
              {item.year && <span> ({item.year})</span>}
              <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                <button onClick={() => setEditing(item)}>Edit</button>
                <button onClick={() => handleDelete(item.id)} disabled={isSaving}>Delete</button>
              </div>
            </>
          )}
        </div>
      ))}

      {showForm ? (
        <div style={{ marginTop: '1rem' }}>
          <ResearchForm isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} style={{ marginTop: '1rem' }}>+ Add Research</button>
      )}
    </div>
  )
}
