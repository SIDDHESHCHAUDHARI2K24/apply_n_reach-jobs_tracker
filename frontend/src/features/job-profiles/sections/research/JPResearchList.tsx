import { useState, useEffect } from 'react'
import { useJPResearch } from './useJPResearch'
import { JPResearchForm } from './JPResearchForm'
import type { JPResearch } from '@features/job-profiles/types'
import type { ImportResult } from '@features/job-profiles/types'
import { Pencil, Trash2, Plus, AlertCircle, Upload, FlaskConical, ExternalLink } from 'lucide-react'

interface Props {
  jobProfileId: string
}

export function JPResearchList({ jobProfileId }: Props) {
  const { items, isLoading, error, load, create, update, remove, importAll } = useJPResearch(jobProfileId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<JPResearch | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setDeleting] = useState<string | null>(null)
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  useEffect(() => { load() }, [load])

  if (isLoading) return (
    <div className="text-sm text-slate-500 py-8">Loading research...</div>
  )

  async function handleCreate(data: Omit<JPResearch, 'id' | 'job_profile_id'>) {
    try {
      setIsSaving(true)
      await create(data)
      setShowForm(false)
    } catch {
    } finally {
      setIsSaving(false)
    }
  }

  async function handleUpdate(data: Omit<JPResearch, 'id' | 'job_profile_id'>) {
    if (!editing) return
    try {
      setIsSaving(true)
      await update(editing.id, data)
      setEditing(null)
    } catch {
    } finally {
      setIsSaving(false)
    }
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

  async function handleImport() {
    try {
      setIsImporting(true)
      setImportResult(null)
      const result = await importAll()
      setImportResult(result)
    } catch {
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-sora text-xl font-semibold text-slate-800">Research</h2>
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
        <p className="text-sm text-slate-400 py-4">No research entries yet.</p>
      )}

      {items.map(item => (
        <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
          {editing?.id === item.id ? (
            <JPResearchForm
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
                    {item.journal && (
                      <span className="text-slate-500 text-sm italic">{item.journal}</span>
                    )}
                    {item.year && (
                      <span className="text-slate-400 text-xs">({item.year})</span>
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
          <JPResearchForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 text-sm text-slate-500 cursor-pointer hover:border-sky-400 hover:bg-sky-50 hover:text-sky-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Research
        </button>
      )}
    </div>
  )
}
