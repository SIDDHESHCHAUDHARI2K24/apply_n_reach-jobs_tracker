import { useState, useEffect } from 'react'
import { useJPCertifications } from './useJPCertifications'
import { JPCertForm } from './JPCertForm'
import type { JPCertification } from '@features/job-profiles/types'
import type { ImportResult } from '@features/job-profiles/types'
import { Pencil, Trash2, Plus, Award, AlertCircle, Upload } from 'lucide-react'

interface Props {
  jobProfileId: string
}

export function JPCertList({ jobProfileId }: Props) {
  const { items, isLoading, error, load, create, update, remove, importAll } = useJPCertifications(jobProfileId)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<JPCertification | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setDeleting] = useState<string | null>(null)
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  useEffect(() => { load() }, [load])

  if (isLoading) return (
    <div className="text-sm text-slate-500 py-8">Loading certifications...</div>
  )

  async function handleCreate(data: Omit<JPCertification, 'id' | 'job_profile_id'>) {
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

  async function handleUpdate(data: Omit<JPCertification, 'id' | 'job_profile_id'>) {
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
    if (!confirm('Delete this certification?')) return
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
        <h2 className="font-sora text-xl font-semibold text-slate-800">Certifications</h2>
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
        <p className="text-sm text-slate-400 py-4">No certifications yet.</p>
      )}

      {items.map(item => (
        <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4">
          {editing?.id === item.id ? (
            <JPCertForm
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
                  {item.credential_url && (
                    <a
                      href={item.credential_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sky-500 text-xs hover:underline mt-0.5 inline-block"
                    >
                      View credential
                    </a>
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
                  disabled={isDeleting === item.id}
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
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <JPCertForm initial={null} isSaving={isSaving} onSave={handleCreate} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <button
          onClick={() => { setShowForm(true); setEditing(null) }}
          className="w-full border-2 border-dashed border-slate-200 rounded-xl p-4 flex items-center justify-center gap-2 text-sm text-slate-500 cursor-pointer hover:border-sky-400 hover:bg-sky-50 hover:text-sky-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Certification
        </button>
      )}
    </div>
  )
}
