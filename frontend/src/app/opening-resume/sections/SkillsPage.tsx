import React from 'react'
import { useParams } from 'react-router-dom'
import { useORSkills } from '@features/opening-resume/sections/useORSkills'

export default function ORSkillsPage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { skills, isLoading, isSaving, error, replaceAll } = useORSkills(openingId ?? '')
  const [text, setTextState] = React.useState('')
  React.useEffect(() => { setTextState(skills.join('\n')) }, [skills])

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Skills</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <p className="text-xs text-slate-500">Enter one skill per line.</p>
        <textarea
          rows={8}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-y"
          value={text}
          onChange={e => setTextState(e.target.value)}
        />
        <div className="flex justify-end">
          <button
            onClick={() => replaceAll(text.split('\n').map(s => s.trim()).filter(Boolean))}
            disabled={isSaving}
            className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            {isSaving ? 'Saving...' : 'Save Skills'}
          </button>
        </div>
      </div>
    </div>
  )
}
