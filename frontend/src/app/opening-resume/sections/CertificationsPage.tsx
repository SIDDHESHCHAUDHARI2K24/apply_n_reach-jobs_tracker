'use client'

import React, { useState } from 'react'
import { Trash2, Plus, Pencil, Award } from 'lucide-react'
import { useORCertifications } from '@features/opening-resume/sections/useORCertifications'
import { ORCertificationForm } from './ORCertificationForm'
import type { ORCertification } from '@features/opening-resume/types'

export default function ORCertificationsPage({ openingId }: { openingId: string }) {
  const { items, isLoading, isSaving, error, create, update, remove } = useORCertifications(openingId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<ORCertification | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleCreate(data: Omit<ORCertification, 'id' | 'resume_id'>) {
    try {
      await create({ ...data, display_order: items.length })
      setShowForm(false)
    } catch { /* error shown by hook */ }
  }

  async function handleUpdate(data: Omit<ORCertification, 'id' | 'resume_id'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch { /* error shown by hook */ }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this certification?')) return
    try {
      await remove(id)
    } catch { /* error shown by hook */ }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Certifications</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No certification entries yet.</p>
      )}

      <div className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            {editing?.id === item.id ? (
              <ORCertificationForm
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
                    <p className="text-sm font-medium text-slate-800">{item.name}</p>
                    {item.issuing_organization && (
                      <p className="text-xs text-slate-500">{item.issuing_organization}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button
                    onClick={() => { setEditing(item); setShowForm(false) }}
                    disabled={isSaving}
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
      </div>

      {showForm ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
          <ORCertificationForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => { setShowForm(true); setEditing(null) }}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Certification
        </button>
      )}
    </div>
  )
}
