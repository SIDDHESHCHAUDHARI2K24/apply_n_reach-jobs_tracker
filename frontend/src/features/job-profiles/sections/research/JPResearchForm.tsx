import React, { useState } from 'react'
import { Globe } from 'lucide-react'
import type { JPResearch } from '@features/job-profiles/types'

type FormFields = {
  title: string
  journal: string
  year: string
  description: string
  url: string
}

function toForm(item: JPResearch | null): FormFields {
  return {
    title: item?.title ?? '',
    journal: item?.journal ?? '',
    year: item?.year ?? '',
    description: item?.description ?? '',
    url: item?.url ?? '',
  }
}

function fromForm(form: FormFields): Omit<JPResearch, 'id' | 'job_profile_id'> {
  return {
    title: form.title,
    journal: form.journal || null,
    year: form.year || null,
    description: form.description || null,
    url: form.url || null,
    institution: null,
    bullet_points: [],
    reference_links: [],
  }
}

interface Props {
  initial: JPResearch | null
  isSaving: boolean
  onSave: (data: Omit<JPResearch, 'id' | 'job_profile_id'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function JPResearchForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      <div>
        <label className={labelClass}>Title <span className="text-red-500">*</span></label>
        <input name="title" value={form.title} onChange={handleChange} required className={inputClass} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Journal</label>
          <input name="journal" value={form.journal} onChange={handleChange} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Year</label>
          <select
            name="year"
            value={form.year}
            onChange={(e) => setForm(f => ({ ...f, year: e.target.value }))}
            className={inputClass}
          >
            <option value="">Select Year</option>
            {Array.from({ length: 51 }, (_, i) => {
              const y = new Date().getFullYear() - i
              return <option key={y} value={String(y)}>{y}</option>
            }).reverse()}
          </select>
        </div>
      </div>

      <div>
        <label className={labelClass}>Description</label>
        <textarea name="description" value={form.description} onChange={handleChange} rows={4} className={`${inputClass} resize-none`} />
      </div>

      <div>
        <label className={labelClass}>URL</label>
        <div className="relative">
          <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input name="url" value={form.url} onChange={handleChange} className={`${inputClass} pl-9`} />
        </div>
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
          onClick={onCancel}
          className="border border-slate-300 text-slate-600 hover:bg-slate-50 px-4 py-2 rounded-lg transition-colors text-sm"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
