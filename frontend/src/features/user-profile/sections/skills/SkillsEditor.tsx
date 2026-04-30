import React, { useState, useEffect } from 'react'
import { useSkills } from './useSkills'

export function SkillsEditor() {
  const { skills, isLoading, isSaving, error, updateSkills } = useSkills()
  const [technicalText, setTechnicalText] = useState('')
  const [competencyText, setCompetencyText] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (skills) {
      setTechnicalText(skills.technical.join(', '))
      setCompetencyText(skills.competency.join(', '))
    }
  }, [skills])

  const parseSkills = (text: string): string[] =>
    text.split(/[,\n]+/).map(s => s.trim()).filter(Boolean)

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(false)
    try {
      await updateSkills({
        technical: parseSkills(technicalText),
        competency: parseSkills(competencyText),
      })
      setSuccess(true)
    } catch {
      // error shown via hook state
    }
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

      <form onSubmit={handleSave} className="space-y-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">
            Technical Skills
          </label>
          <textarea
            value={technicalText}
            onChange={e => { setTechnicalText(e.target.value); setSuccess(false) }}
            rows={4}
            placeholder="Python, FastAPI, PostgreSQL, React..."
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">
            Competencies
          </label>
          <textarea
            value={competencyText}
            onChange={e => { setCompetencyText(e.target.value); setSuccess(false) }}
            rows={4}
            placeholder="Team Leadership, Project Management..."
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
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
