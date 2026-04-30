import React, { useState } from 'react'
import type { Experience } from '@features/user-profile/types'

type FormFields = {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string
  context: string
  bullet_points: string
}

function toForm(item?: Experience): FormFields {
  return {
    company: item?.company ?? '',
    title: item?.title ?? '',
    location: item?.location ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    context: item?.context ?? '',
    bullet_points: item?.bullet_points.join('\n') ?? '',
  }
}

function fromForm(form: FormFields): Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    company: form.company,
    title: form.title,
    location: form.location || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    is_current: false,
    context: form.context || null,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
  }
}

interface Props {
  initial?: Experience
  isSaving: boolean
  onSave: (data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function ExperienceForm({ initial, isSaving, onSave, onCancel }: Props) {
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Company *</label>
          <input name="company" value={form.company} onChange={handleChange} required className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Title *</label>
          <input name="title" value={form.title} onChange={handleChange} required className={inputClass} />
        </div>
      </div>

      <div>
        <label className={labelClass}>Location</label>
        <input name="location" value={form.location} onChange={handleChange} className={inputClass} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Start Date</label>
          <input name="start_date" value={form.start_date} onChange={handleChange} placeholder="MM/YYYY" className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>End Date</label>
          <input name="end_date" value={form.end_date} onChange={handleChange} placeholder="MM/YYYY" className={inputClass} />
        </div>
      </div>

      <div>
        <label className={labelClass}>Job Description / Context</label>
        <textarea name="context" value={form.context} onChange={handleChange} rows={5} maxLength={10000} placeholder="Describe the role, team, and work context..." className={`${inputClass} resize-none`} />
        <p className="text-xs text-slate-400 mt-1 text-right">{form.context.length} / 10,000</p>
      </div>

      <div>
        <label className={labelClass}>Bullet Points (one per line)</label>
        <textarea name="bullet_points" value={form.bullet_points} onChange={handleChange} rows={4} className={`${inputClass} resize-none`} />
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
