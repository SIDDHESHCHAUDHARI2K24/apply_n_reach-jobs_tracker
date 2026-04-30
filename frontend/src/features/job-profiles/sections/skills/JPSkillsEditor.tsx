import { useState, useEffect } from 'react'
import { useJPSkills } from './useJPSkills'

export function JPSkillsEditor({ jobProfileId }: { jobProfileId: string }) {
  const { skills, isLoading, error, load, update, importAll } = useJPSkills(jobProfileId)
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [result, setResult] = useState<{ imported: number; skipped: number } | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    setValue(skills.join(', '))
  }, [skills])

  const parseSkills = (text: string): string[] =>
    text.split(/[,\n]+/).map(s => s.trim()).filter(Boolean)

  async function handleSave() {
    setIsSaving(true)
    setSaveSuccess(false)
    try {
      await update(parseSkills(value))
      setSaveSuccess(true)
      setEditing(false)
    } catch {
      // error shown via hook state
    } finally {
      setIsSaving(false)
    }
  }

  async function handleImport() {
    setIsImporting(true)
    setSaveSuccess(false)
    try {
      const res = await importAll()
      setResult({ imported: res.imported_count, skipped: res.skipped_count })
    } catch {
      // error shown via hook state
    } finally {
      setIsImporting(false)
    }
  }

  function handleCancel() {
    setValue(skills.join(', '))
    setEditing(false)
    setSaveSuccess(false)
  }

  function startEditing() {
    setValue(skills.join(', '))
    setEditing(true)
    setSaveSuccess(false)
  }

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">
      Loading skills...
    </div>
  )

  return (
    <div className="space-y-5">
      {error && (
        <div role="alert" className="px-4 py-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}
      {saveSuccess && (
        <div className="px-4 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
          Skills saved successfully.
        </div>
      )}
      {result && (
        <div className="px-4 py-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 text-sm">
          Imported {result.imported} skill{result.imported !== 1 ? 's' : ''}
          {result.skipped > 0 && ` (${result.skipped} skipped)`}.
        </div>
      )}

      {editing ? (
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">
              Skills
            </label>
            <textarea
              value={value}
              onChange={e => { setValue(e.target.value); setSaveSuccess(false) }}
              rows={6}
              placeholder="Python, FastAPI, PostgreSQL, React..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
            <p className="text-xs text-slate-400">Separate skills with commas or new lines.</p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
            >
              {isSaving ? 'Saving...' : 'Save Skills'}
            </button>
            <button
              onClick={handleCancel}
              disabled={isSaving}
              className="bg-white hover:bg-slate-50 text-slate-700 font-semibold px-4 py-2 rounded-lg border border-slate-300 transition-colors disabled:opacity-50 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {skills.length === 0 ? (
              <p className="text-sm text-slate-400">No skills added yet.</p>
            ) : (
              skills.map(skill => (
                <span
                  key={skill}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200"
                >
                  {skill}
                </span>
              ))
            )}
          </div>

          <div className="flex gap-2">
            <button
              onClick={startEditing}
              className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors text-sm"
            >
              Edit Skills
            </button>
            <button
              onClick={handleImport}
              disabled={isImporting}
              className="bg-white hover:bg-slate-50 text-slate-700 font-semibold px-4 py-2 rounded-lg border border-slate-300 transition-colors disabled:opacity-50 text-sm"
            >
              {isImporting ? 'Importing...' : 'Import Skills from User Profile'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
