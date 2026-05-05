import React, { useState } from 'react'
import type { ORResearch } from '@features/opening-resume/types'

type FormFields = {
  title: string
  publication: string
  published_date: string
  description: string
  url: string
}

function toForm(item: ORResearch | null): FormFields {
  return {
    title: item?.title ?? '',
    publication: item?.publication ?? '',
    published_date: item?.published_date ?? '',
    description: item?.description ?? '',
    url: item?.url ?? '',
  }
}

function fromForm(form: FormFields): Omit<ORResearch, 'id' | 'resume_id'> {
  return {
    title: form.title,
    publication: form.publication || null,
    published_date: form.published_date || null,
    description: form.description || null,
    url: form.url || null,
    display_order: 0,
  }
}

interface Props {
  initial: ORResearch | null
  isSaving: boolean
  onSave: (data: Omit<ORResearch, 'id' | 'resume_id'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function ORResearchForm({ initial, isSaving, onSave, onCancel }: Props) {
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

      <div>
        <label className={labelClass}>Publication</label>
        <input name="publication" value={form.publication} onChange={handleChange} placeholder="Journal, conference, etc." className={inputClass} />
      </div>

      <div>
        <label className={labelClass}>Published Date</label>
        <input name="published_date" value={form.published_date} onChange={handleChange} placeholder="e.g. 2024 or June 2024" className={inputClass} />
      </div>

      <div>
        <label className={labelClass}>Description</label>
        <textarea name="description" value={form.description} onChange={handleChange} rows={4} className={`${inputClass} resize-none`} />
      </div>

      <div>
        <label className={labelClass}>URL</label>
        <input name="url" value={form.url} onChange={handleChange} placeholder="https://doi.org/..." className={inputClass} />
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
