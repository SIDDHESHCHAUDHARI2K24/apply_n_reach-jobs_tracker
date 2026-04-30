import { useState } from 'react'
import { useEducation } from './useEducation'
import { EducationForm } from './EducationForm'
import type { Education } from '@features/user-profile/types'
import { Pencil, Trash2, Plus, AlertCircle } from 'lucide-react'

export function EducationList() {
  const { items, isLoading, isSaving, error, create, update, remove } = useEducation()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Education | null>(null)

  if (isLoading) return (
    <div className="text-sm text-slate-500 py-8">Loading education...</div>
  )

  async function handleCreate(data: Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    try {
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleUpdate(data: Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this education entry?')) return
    try {
      await remove(id)
    } catch {
      // error displayed by hook's error state
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="font-sora text-xl font-semibold text-slate-800">Education</h2>

      {error && (
        <div role="alert" className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {items.map(item => (
        <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
          {editing?.id === item.id ? (
            <EducationForm
              initial={item}
              isSaving={isSaving}
              onSave={handleUpdate}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold text-slate-800">{item.institution}</p>
                <p className="text-slate-600 text-sm">{item.degree}{item.field_of_study && ` — ${item.field_of_study}`}</p>
                {(item.start_date || item.end_date) && (
                  <p className="text-slate-400 text-xs mt-1">
                    {item.start_date ?? ''}{item.start_date && item.end_date ? ' – ' : ''}{item.end_date ?? ''}
                  </p>
                )}
              </div>
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => setEditing(item)}
                  className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                  aria-label="Edit"
                >
                  <Pencil className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={isSaving}
                  className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  aria-label="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      ))}

      {showForm ? (
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <EducationForm isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 text-sm text-slate-500 cursor-pointer hover:border-sky-400 hover:bg-sky-50 hover:text-sky-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Education
        </button>
      )}
    </div>
  )
}
