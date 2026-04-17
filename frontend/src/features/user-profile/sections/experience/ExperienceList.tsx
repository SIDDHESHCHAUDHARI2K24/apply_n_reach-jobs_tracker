import { useState } from 'react'
import { useExperience } from './useExperience'
import { ExperienceForm } from './ExperienceForm'
import type { Experience } from '@features/user-profile/types'

export function ExperienceList() {
  const { items, isLoading, isSaving, error, create, update, remove } = useExperience()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Experience | null>(null)

  if (isLoading) return <div>Loading experience...</div>

  async function handleCreate(data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    try {
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleUpdate(data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this experience entry?')) return
    try {
      await remove(id)
    } catch {
      // error displayed by hook's error state
    }
  }

  return (
    <div>
      <h2>Experience</h2>
      {error && <div role="alert" style={{ color: 'red' }}>{error}</div>}

      {items.map(item => (
        <div key={item.id} style={{ border: '1px solid #e5e7eb', padding: '1rem', marginBottom: '0.5rem', borderRadius: '4px' }}>
          {editing?.id === item.id ? (
            <ExperienceForm
              initial={item}
              isSaving={isSaving}
              onSave={handleUpdate}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <>
              <strong>{item.company}</strong> — {item.title}
              {item.is_current && <span> (Current)</span>}
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
          <ExperienceForm isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} style={{ marginTop: '1rem' }}>+ Add Experience</button>
      )}
    </div>
  )
}
