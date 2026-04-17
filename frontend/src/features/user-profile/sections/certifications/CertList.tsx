import { useState } from 'react'
import { Pencil, Trash2, Award, Plus } from 'lucide-react'
import { useCertifications } from './useCertifications'
import { CertForm } from './CertForm'
import type { Certification } from '@features/user-profile/types'

export function CertList() {
  const { items, isLoading, isSaving, error, create, update, remove } = useCertifications()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Certification | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">
      Loading certifications...
    </div>
  )

  async function handleCreate(data: Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    try {
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleUpdate(data: Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this certification?')) return
    try {
      await remove(id)
    } catch {
      // error displayed by hook's error state
    }
  }

  return (
    <div className="space-y-3">
      {error && (
        <div role="alert" className="px-4 py-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      {items.map(item => (
        <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4 mb-3">
          {editing?.id === item.id ? (
            <CertForm
              initial={item}
              isSaving={isSaving}
              onSave={handleUpdate}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 min-w-0">
                <div className="mt-0.5 flex-shrink-0 w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center">
                  <Award size={16} className="text-amber-500" />
                </div>
                <div className="min-w-0">
                  <p className="font-semibold text-slate-800 text-sm leading-snug">{item.name}</p>
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5">
                    {item.issuing_organization && (
                      <span className="text-slate-500 text-sm">{item.issuing_organization}</span>
                    )}
                    {item.issue_date && (
                      <span className="text-slate-400 text-xs">Issued {item.issue_date}</span>
                    )}
                    {item.expiry_date && (
                      <span className="text-slate-400 text-xs">· Expires {item.expiry_date}</span>
                    )}
                  </div>
                  {item.credential_id && (
                    <p className="text-slate-400 text-xs mt-0.5">ID: {item.credential_id}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => { setEditing(item); setShowForm(false) }}
                  className="p-1.5 rounded-md text-slate-400 hover:text-sky-500 hover:bg-sky-50 transition-colors"
                  aria-label="Edit certification"
                >
                  <Pencil size={15} />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={isSaving}
                  className="p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50"
                  aria-label="Delete certification"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          )}
        </div>
      ))}

      {showForm ? (
        <div className="bg-white rounded-xl border border-slate-200 p-4 mb-3">
          <CertForm isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => { setShowForm(true); setEditing(null) }}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 cursor-pointer hover:border-sky-400 hover:bg-sky-50 text-slate-500 hover:text-sky-600 transition-colors"
        >
          <Plus size={16} />
          <span className="text-sm font-medium">Add Certification</span>
        </button>
      )}
    </div>
  )
}
