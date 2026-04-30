import React, { useState } from 'react'
import { Globe } from 'lucide-react'
import type { Research } from '@features/user-profile/types'

type FormFields = {
  title: string
  journal: string
  year: string
  description: string
  url: string
}

function toForm(item?: Research): FormFields {
  return {
    title: item?.title ?? '',
    journal: item?.journal ?? '',
    year: item?.year ?? '',
    description: item?.description ?? '',
    url: item?.url ?? '',
  }
}

function fromForm(form: FormFields): Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    title: form.title,
    journal: form.journal || null,
    year: form.year || null,
    description: form.description || null,
    url: form.url || null,
  }
}

interface Props {
  initial?: Research
  isSaving: boolean
  onSave: (data: Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

export function ResearchForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  const fieldClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
  const labelClass = 'block text-sm font-medium text-slate-700'

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      {/* Title */}
      <div className="space-y-1">
        <label className={labelClass}>Title <span className="text-red-500">*</span></label>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          required
          placeholder="e.g. Deep Learning for Medical Imaging"
          className={fieldClass}
        />
      </div>

      {/* Journal */}
      <div className="space-y-1">
        <label className={labelClass}>Journal / Conference</label>
        <input
          name="journal"
          value={form.journal}
          onChange={handleChange}
          placeholder="e.g. Nature Machine Intelligence"
          className={fieldClass}
        />
      </div>

      {/* Year */}
      <div className="space-y-1" style={{ maxWidth: '160px' }}>
        <label className={labelClass}>Year</label>
        <input
          name="year"
          value={form.year}
          onChange={handleChange}
          maxLength={4}
          placeholder="2024"
          className={fieldClass}
        />
      </div>

      {/* Description */}
      <div className="space-y-1">
        <label className={labelClass}>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          rows={3}
          placeholder="Summary of the research..."
          className={fieldClass}
        />
      </div>

      {/* URL */}
      <div className="space-y-1">
        <label className={labelClass}>URL</label>
        <div className="relative">
          <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            name="url"
            value={form.url}
            onChange={handleChange}
            placeholder="https://doi.org/..."
            className={`${fieldClass} pl-9`}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 pt-1">
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
