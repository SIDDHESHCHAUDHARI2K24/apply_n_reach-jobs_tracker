import { useState } from 'react'
import { Pencil, Trash2, FolderKanban, Plus } from 'lucide-react'
import { useProjects } from './useProjects'
import { ProjectForm } from './ProjectForm'
import type { Project } from '@features/user-profile/types'

export function ProjectList() {
  const { items, isLoading, isSaving, error, create, update, remove } = useProjects()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Project | null>(null)

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">
      Loading projects...
    </div>
  )

  async function handleCreate(data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    try {
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleUpdate(data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) {
    if (!editing) return
    try {
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this project?')) return
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
            <ProjectForm
              initial={item}
              isSaving={isSaving}
              onSave={handleUpdate}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 min-w-0">
                <div className="mt-0.5 flex-shrink-0 w-8 h-8 rounded-lg bg-sky-50 flex items-center justify-center">
                  <FolderKanban size={16} className="text-sky-500" />
                </div>
                <div className="min-w-0">
                  <p className="font-semibold text-slate-800 text-sm leading-snug">{item.title}</p>
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
                      {item.start_date ?? ''}
                      {item.start_date && item.end_date ? ' – ' : ''}
                      {item.end_date ?? ''}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => { setEditing(item); setShowForm(false) }}
                  className="p-1.5 rounded-md text-slate-400 hover:text-sky-500 hover:bg-sky-50 transition-colors"
                  aria-label="Edit project"
                >
                  <Pencil size={15} />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={isSaving}
                  className="p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50"
                  aria-label="Delete project"
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
          <ProjectForm isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => { setShowForm(true); setEditing(null) }}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 cursor-pointer hover:border-sky-400 hover:bg-sky-50 text-slate-500 hover:text-sky-600 transition-colors"
        >
          <Plus size={16} />
          <span className="text-sm font-medium">Add Project</span>
        </button>
      )}
    </div>
  )
}
