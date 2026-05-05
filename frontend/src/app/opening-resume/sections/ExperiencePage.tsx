'use client'

import React, { useState } from 'react'
import { Pencil, Trash2, Plus } from 'lucide-react'
import { useORExperience } from '@features/opening-resume/sections/useORExperience'
import { ORExperienceForm } from './ORExperienceForm'
import type { ORExperience } from '@features/opening-resume/types'

export default function ORExperiencePage({ openingId }: { openingId: string }) {
  const { items, isLoading, isSaving, error, create, update, remove } = useORExperience(openingId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<ORExperience | null>(null)
  const [isDeleting, setDeleting] = useState<string | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleCreate(data: Omit<ORExperience, 'id' | 'resume_id' | 'display_order'>) {
    try {
      await create({ ...data, display_order: items.length })
      setShowForm(false)
    } catch { /* error shown by hook */ }
  }

  async function handleUpdate(data: Omit<ORExperience, 'id' | 'resume_id' | 'display_order'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch { /* error shown by hook */ }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this experience entry?')) return
    try {
      setDeleting(id)
      await remove(id)
    } catch {
      // error shown by hook
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Experience</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No experience entries yet.</p>
      )}

      <div className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
            {editing?.id === item.id ? (
              <ORExperienceForm
                initial={item}
                isSaving={isSaving}
                onSave={handleUpdate}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-800">{item.company}</p>
                  <p className="text-slate-600 text-sm">
                    {item.title}
                    {item.is_current && <span className="ml-2 text-xs bg-sky-50 text-sky-600 px-1.5 py-0.5 rounded font-medium">Current</span>}
                  </p>
                  {item.location && (
                    <p className="text-slate-400 text-xs mt-1">{item.location}</p>
                  )}
                  {(item.start_date || item.end_date) && (
                    <p className="text-slate-400 text-xs mt-1">
                      {item.start_date ?? ''}{item.start_date && (item.end_date || item.is_current) ? ' – ' : ''}{item.is_current ? 'Present' : (item.end_date ?? '')}
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
                    disabled={isDeleting === item.id}
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
      </div>

      {showForm ? (
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <ORExperienceForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Experience
        </button>
      )}
    </div>
  )
}
