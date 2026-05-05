'use client'

import React, { useState } from 'react'
import { Pencil, Trash2, Plus, Globe } from 'lucide-react'
import { useORProjects } from '@features/opening-resume/sections/useORProjects'
import { ORProjectForm } from './ORProjectForm'
import type { ORProject } from '@features/opening-resume/types'

export default function ORProjectsPage({ openingId }: { openingId: string }) {
  const { items, isLoading, isSaving, error, create, update, remove } = useORProjects(openingId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<ORProject | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleCreate(data: Omit<ORProject, 'id' | 'resume_id'>) {
    await create(data)
    setShowForm(false)
  }

  async function handleUpdate(data: Omit<ORProject, 'id' | 'resume_id'>) {
    if (!editing) return
    await update(editing.id, data)
    setEditing(null)
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this project?')) return
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
        <h3 className="font-sora text-base font-semibold text-slate-800">Projects</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No project entries yet.</p>
      )}

      <div className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
            {editing?.id === item.id ? (
              <ORProjectForm
                initial={item}
                isSaving={isSaving}
                onSave={handleUpdate}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="font-semibold text-slate-800">{item.title}</p>
                  {item.description && (
                    <p className="text-slate-500 text-sm mt-0.5 line-clamp-2">{item.description}</p>
                  )}
                  {item.technologies && item.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {item.technologies.map(tech => (
                        <span
                          key={tech}
                          className="inline-block px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-medium"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                  {(item.start_date || item.end_date) && (
                    <p className="text-slate-400 text-xs mt-1.5">
                      {item.start_date ?? ''}{item.start_date && item.end_date ? ' - ' : ''}{item.end_date ?? ''}
                    </p>
                  )}
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sky-600 hover:text-sky-700 text-xs mt-1.5"
                    >
                      <Globe className="h-3 w-3" />
                      {item.url}
                    </a>
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
          <ORProjectForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Project
        </button>
      )}
    </div>
  )
}
