'use client'

import React from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { useORSkills } from '@features/opening-resume/sections/useORSkills'

export default function ORSkillsPage({ openingId }: { openingId: string }) {
  const { skills, isLoading, isSaving, error, create, remove } = useORSkills(openingId)
  const [showForm, setShowForm] = React.useState(false)
  const [form, setForm] = React.useState({ category: '', name: '', proficiency_level: '' })

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

      <div className="space-y-2">
        {skills.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm px-4 py-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-800">{item.name}</p>
              <p className="text-xs text-slate-500">{item.category}{item.proficiency_level ? ` · ${item.proficiency_level}` : ''}</p>
            </div>
            <button
              onClick={() => remove(item.id).catch(() => {})}
              disabled={isSaving}
              className="p-1.5 text-slate-400 hover:text-red-500 transition-colors disabled:opacity-50 rounded-lg hover:bg-red-50"
              aria-label="Delete skill entry"
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}
      </div>

      {showForm ? (
        <form
          onSubmit={async (event) => {
            event.preventDefault()
            if (!form.category.trim() || !form.name.trim()) return
            try {
              await create({
                category: form.category.trim(),
                name: form.name.trim(),
                proficiency_level: form.proficiency_level.trim() || null,
                display_order: skills.length,
              })
              setForm({ category: '', name: '', proficiency_level: '' })
              setShowForm(false)
            } catch {
              // Error handled in hook
            }
          }}
          className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3"
        >
          <input
            required
            placeholder="Category (e.g. Programming)"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.category}
            onChange={e => setForm(current => ({ ...current, category: e.target.value }))}
          />
          <input
            required
            placeholder="Skill name"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.name}
            onChange={e => setForm(current => ({ ...current, name: e.target.value }))}
          />
          <input
            placeholder="Proficiency (optional)"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.proficiency_level}
            onChange={e => setForm(current => ({ ...current, proficiency_level: e.target.value }))}
          />
          <button
            type="submit"
            disabled={isSaving}
            className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            {isSaving ? 'Saving...' : 'Save Skills'}
          </button>
        </form>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Skill
        </button>
      )}
    </div>
  )
}
