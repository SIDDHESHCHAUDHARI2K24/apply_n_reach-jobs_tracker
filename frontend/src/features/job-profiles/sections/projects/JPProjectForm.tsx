import React, { useState } from 'react'
import type { JPProject } from '@features/job-profiles/types'
import { MonthYearPicker } from '../../../../components/MonthYearPicker'

type FormFields = {
  title: string
  description: string
  url: string
  technologies: string
  start_date: string
  end_date: string
}

function toForm(item: JPProject | null): FormFields {
  return {
    title: item?.title ?? '',
    description: item?.description ?? '',
    url: item?.url ?? '',
    technologies: item?.technologies?.join('\n') ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
  }
}

function fromForm(form: FormFields): Omit<JPProject, 'id' | 'job_profile_id'> {
  return {
    title: form.title,
    description: form.description || null,
    url: form.url || null,
    technologies: form.technologies ? form.technologies.split('\n').filter(l => l.trim()) : [],
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    bullet_points: [],
  }
}

interface Props {
  initial: JPProject | null
  isSaving: boolean
  onSave: (data: Omit<JPProject, 'id' | 'job_profile_id'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function JPProjectForm({ initial, isSaving, onSave, onCancel }: Props) {
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
        <label className={labelClass}>Title *</label>
        <input name="title" value={form.title} onChange={handleChange} required className={inputClass} />
      </div>

      <div>
        <label className={labelClass}>Description</label>
        <textarea name="description" value={form.description} onChange={handleChange} rows={3} className={`${inputClass} resize-none`} />
      </div>

      <div>
        <label className={labelClass}>URL</label>
        <input name="url" value={form.url} onChange={handleChange} placeholder="https://github.com/..." className={inputClass} />
      </div>

      <div>
        <label className={labelClass}>Technologies (one per line)</label>
        <textarea name="technologies" value={form.technologies} onChange={handleChange} rows={4} className={`${inputClass} resize-none`} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Start Date</label>
          <MonthYearPicker
            value={form.start_date}
            onChange={(value: string) => setForm(f => ({ ...f, start_date: value }))}
          />
        </div>
        <div>
          <label className={labelClass}>End Date</label>
          <MonthYearPicker
            value={form.end_date}
            onChange={(value: string) => setForm(f => ({ ...f, end_date: value }))}
          />
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
