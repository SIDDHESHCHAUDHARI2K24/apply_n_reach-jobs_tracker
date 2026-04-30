import { useState, useEffect } from 'react'
import { useJPProjects } from './useJPProjects'
import { JPProjectForm } from './JPProjectForm'
import type { JPProject } from '@features/job-profiles/types'
import type { ImportResult } from '@features/job-profiles/types'
import { Pencil, Trash2, Plus, AlertCircle, Upload, Globe } from 'lucide-react'

interface Props {
  jobProfileId: string
}

export function JPProjectList({ jobProfileId }: Props) {
  const { items, isLoading, error, load, create, update, remove, importAll } = useJPProjects(jobProfileId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<JPProject | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setDeleting] = useState<string | null>(null)
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  useEffect(() => { load() }, [load])

  if (isLoading) return (
    <div className="text-sm text-slate-500 py-8">Loading projects...</div>
  )

  async function handleCreate(data: Omit<JPProject, 'id' | 'job_profile_id'>) {
    try {
      setIsSaving(true)
      await create(data)
      setShowForm(false)
    } catch {
      // error displayed by hook's error state
    } finally {
      setIsSaving(false)
    }
  }

  async function handleUpdate(data: Omit<JPProject, 'id' | 'job_profile_id'>) {
    if (!editing) return
    try {
      setIsSaving(true)
      await update(editing.id, data)
      setEditing(null)
    } catch {
      // error displayed by hook's error state
    } finally {
      setIsSaving(false)
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this project?')) return
    try {
      setDeleting(id)
      await remove(id)
    } catch {
      // error displayed by hook's error state
    } finally {
      setDeleting(null)
    }
  }

  async function handleImport() {
    try {
      setIsImporting(true)
      setImportResult(null)
      const result = await importAll()
      setImportResult(result)
    } catch {
      // error displayed by hook's error state
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-sora text-xl font-semibold text-slate-800">Projects</h2>
        <button
          onClick={handleImport}
          disabled={isImporting}
          className="flex items-center gap-1.5 text-xs font-medium text-sky-600 hover:text-sky-700 hover:bg-sky-50 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
        >
          <Upload className="h-3.5 w-3.5" />
          {isImporting ? 'Importing...' : 'Import from Profile'}
        </button>
      </div>

      {error && (
        <div role="alert" className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {importResult && (
        <div className="bg-sky-50 border border-sky-200 rounded-lg px-4 py-3 text-sky-700 text-sm">
          Imported {importResult.imported_count} item{importResult.imported_count !== 1 ? 's' : ''}
          {importResult.skipped_count > 0 && `, ${importResult.skipped_count} skipped`}.
        </div>
      )}

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400 py-4">No projects yet.</p>
      )}

      {items.map(item => (
        <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
          {editing?.id === item.id ? (
            <JPProjectForm
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
                    {item.start_date ?? ''}{item.start_date && item.end_date ? ' – ' : ''}{item.end_date ?? ''}
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

      {showForm ? (
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <JPProjectForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 text-sm text-slate-500 cursor-pointer hover:border-sky-400 hover:bg-sky-50 hover:text-sky-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Project
        </button>
      )}
    </div>
  )
}
