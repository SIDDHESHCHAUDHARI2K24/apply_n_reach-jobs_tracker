'use client'

import React, { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { useORSkills } from '@features/opening-resume/sections/useORSkills'

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

const proficiencyColors: Record<string, string> = {
  Expert: 'bg-purple-100 text-purple-700',
  Advanced: 'bg-blue-100 text-blue-700',
  Intermediate: 'bg-green-100 text-green-700',
  Beginner: 'bg-slate-100 text-slate-600',
  Native: 'bg-emerald-100 text-emerald-700',
  Fluent: 'bg-teal-100 text-teal-700',
}

function proficiencyBadge(level: string | null) {
  if (!level) return null
  const color = proficiencyColors[level] ?? 'bg-slate-100 text-slate-600'
  return (
    <span className={`inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${color}`}>
      {level}
    </span>
  )
}

function groupByCategory(skills: { category: string; name: string; proficiency_level: string | null; id: string }[]) {
  const groups: Record<string, typeof skills> = {}
  for (const s of skills) {
    const cat = s.category || 'Other'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(s)
  }
  return groups
}

export default function ORSkillsPage({ openingId }: { openingId: string }) {
  const { skills, isLoading, isSaving, error, create, remove } = useORSkills(openingId)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ category: '', name: '', proficiency_level: '' })

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  const groups = groupByCategory(skills)

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Skills</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {skills.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No skills added yet.</p>
      )}

      {Object.entries(groups).map(([category, catSkills]) => (
        <div key={category} className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">{category}</h4>
          <div className="grid gap-2">
            {catSkills.map(item => (
              <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm px-4 py-3 flex items-center justify-between gap-2">
                <div className="min-w-0 flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium text-slate-800">{item.name}</span>
                  {proficiencyBadge(item.proficiency_level)}
                </div>
                <button
                  onClick={() => remove(item.id).catch(() => {})}
                  disabled={isSaving}
                  className="p-1.5 text-slate-400 hover:text-red-500 transition-colors disabled:opacity-50 rounded-lg hover:bg-red-50 flex-shrink-0"
                  aria-label="Delete skill entry"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}

      {showForm ? (
        <form
          onSubmit={async (e) => {
            e.preventDefault()
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
              // error shown by hook
            }
          }}
          className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3"
        >
          <div>
            <label className={labelClass}>Category <span className="text-red-500">*</span></label>
            <input
              required
              placeholder="e.g. Programming Languages"
              className={inputClass}
              value={form.category}
              onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
            />
          </div>
          <div>
            <label className={labelClass}>Skill Name <span className="text-red-500">*</span></label>
            <input
              required
              placeholder="e.g. Python"
              className={inputClass}
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className={labelClass}>Proficiency Level</label>
            <input
              placeholder="e.g. Expert, Advanced, Intermediate, Beginner"
              className={inputClass}
              value={form.proficiency_level}
              onChange={e => setForm(f => ({ ...f, proficiency_level: e.target.value }))}
            />
          </div>
          <div className="flex gap-2 pt-1">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="border border-slate-300 text-slate-600 hover:bg-slate-50 px-4 py-2 rounded-lg transition-colors text-sm"
            >
              Cancel
            </button>
          </div>
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
