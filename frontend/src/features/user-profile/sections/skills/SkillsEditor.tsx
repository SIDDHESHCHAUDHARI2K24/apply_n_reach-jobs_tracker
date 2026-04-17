import React, { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { useSkills } from './useSkills'

export function SkillsEditor() {
  const { skills, isLoading, isSaving, error, replaceAll } = useSkills()
  const [text, setText] = useState('')
  const [success, setSuccess] = useState(false)
  const [showBulkEdit, setShowBulkEdit] = useState(false)

  useEffect(() => {
    setText(skills.join('\n'))
  }, [skills])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(false)
    const newSkills = text.split('\n').map(s => s.trim()).filter(Boolean)
    try {
      await replaceAll(newSkills)
      setSuccess(true)
    } catch {
      // error shown via hook state
    }
  }

  const parsedSkills = text.split('\n').map(s => s.trim()).filter(Boolean)

  function removeSkill(skill: string) {
    const updated = parsedSkills.filter(s => s !== skill)
    setText(updated.join('\n'))
    setSuccess(false)
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
      {success && (
        <div className="px-4 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
          Skills saved successfully.
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Tag cloud */}
        {parsedSkills.length > 0 ? (
          <div className="flex flex-wrap gap-2 p-4 bg-slate-50 rounded-xl border border-slate-200 min-h-[60px]">
            {parsedSkills.map(skill => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-sky-100 text-sky-700 text-sm font-medium"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="text-sky-500 hover:text-sky-700 transition-colors"
                  aria-label={`Remove ${skill}`}
                >
                  <X size={12} className="cursor-pointer" />
                </button>
              </span>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-sm text-center">
            No skills added yet. Use bulk edit below to add skills.
          </div>
        )}

        {/* Bulk edit toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowBulkEdit(v => !v)}
            className="text-sm text-sky-600 hover:text-sky-700 font-medium transition-colors"
          >
            {showBulkEdit ? 'Hide bulk edit' : 'Bulk edit'}
          </button>

          {showBulkEdit && (
            <div className="mt-2 space-y-1">
              <label className="block text-sm font-medium text-slate-700">
                Skills <span className="text-xs font-normal text-slate-400">(one per line)</span>
              </label>
              <textarea
                value={text}
                onChange={e => { setText(e.target.value); setSuccess(false) }}
                rows={10}
                placeholder={"React\nTypeScript\nPython\nFastAPI"}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={isSaving}
          className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
        >
          {isSaving ? 'Saving...' : 'Save Skills'}
        </button>
      </form>
    </div>
  )
}
