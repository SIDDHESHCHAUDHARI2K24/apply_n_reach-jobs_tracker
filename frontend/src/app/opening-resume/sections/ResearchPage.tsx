'use client'

import React, { useState } from 'react'
import { Pencil, Trash2, Plus, FlaskConical, ExternalLink } from 'lucide-react'
import { useORResearch } from '@features/opening-resume/sections/useORResearch'
import { ORResearchForm } from './ORResearchForm'
import type { ORResearch } from '@features/opening-resume/types'

export default function ORResearchPage({ openingId }: { openingId: string }) {
  const { items, isLoading, isSaving, error, create, update, remove } = useORResearch(openingId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<ORResearch | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleCreate(data: Omit<ORResearch, 'id' | 'resume_id'>) {
    await create(data)
    setShowForm(false)
  }

  async function handleUpdate(data: Omit<ORResearch, 'id' | 'resume_id'>) {
    if (!editing) return
    await update(editing.id, data)
    setEditing(null)
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this research entry?')) return
    try {
      setDeleting(id)
      await remove(id)
    } catch {
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Research</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No research entries yet.</p>
      )}

      <div className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
            {editing?.id === item.id ? (
              <ORResearchForm
                initial={item}
                isSaving={isSaving}
                onSave={handleUpdate}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 min-w-0">
                  <div className="mt-0.5 flex-shrink-0 w-8 h-8 rounded-lg bg-sky-50 flex items-center justify-center">
                    <FlaskConical size={16} className="text-sky-500" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-800 text-sm">{item.title}</p>
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5">
                      {item.publication && (
                        <span className="text-slate-500 text-sm italic">{item.publication}</span>
                      )}
                      {item.published_date && (
                        <span className="text-slate-400 text-xs">({item.published_date})</span>
                      )}
                    </div>
                    {item.description && (
                      <p className="text-slate-500 text-sm mt-1 line-clamp-2">{item.description}</p>
                    )}
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-sky-600 hover:text-sky-700 hover:underline mt-1"
                      >
                        <ExternalLink size={12} />
                        View Publication
                      </a>
                    )}
                  </div>
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
                    disabled={deleting === item.id}
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
          <ORResearchForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Research
        </button>
      )}
    </div>
  )
}
