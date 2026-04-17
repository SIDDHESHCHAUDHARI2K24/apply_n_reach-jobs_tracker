import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Trash2, Plus } from 'lucide-react'
import { useORExperience } from '@features/opening-resume/sections/useORExperience'

export default function ORExperiencePage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { items, isLoading, isSaving, error, create, remove } = useORExperience(openingId ?? '')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ company: '', title: '' })

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!form.company.trim() || !form.title.trim()) return
    try {
      await create({ company: form.company.trim(), title: form.title.trim(), location: null, start_date: null, end_date: null, is_current: false, bullet_points: [] })
      setForm({ company: '', title: '' })
      setShowForm(false)
    } catch { /* error shown by hook */ }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Experience</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Independent snapshot — changes here do not affect your source profile.</p>
      </div>

      {items.length === 0 && !showForm && (
        <p className="text-sm text-slate-400">No experience entries yet.</p>
      )}

      <div className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl border border-slate-200 shadow-sm px-4 py-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-800">{item.company}</p>
              <p className="text-xs text-slate-500">{item.title}</p>
            </div>
            <button
              onClick={() => remove(item.id).catch(() => {})}
              disabled={isSaving}
              className="p-1.5 text-slate-400 hover:text-red-500 transition-colors disabled:opacity-50 rounded-lg hover:bg-red-50"
              aria-label="Delete experience entry"
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3">
          <input
            required
            placeholder="Company"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.company}
            onChange={e => setForm(f => ({ ...f, company: e.target.value }))}
          />
          <input
            required
            placeholder="Title"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {!showForm && (
        <button
          onClick={() => setShowForm(s => !s)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-sky-400 hover:text-sky-500 transition-colors text-sm font-medium"
        >
          <Plus size={15} />
          Add Experience
        </button>
      )}
    </div>
  )
}
