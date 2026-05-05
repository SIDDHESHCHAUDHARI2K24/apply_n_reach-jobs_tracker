import React, { useState } from 'react'
import type { ORExperience } from '@features/opening-resume/types'
import { MonthYearPicker } from '../../../components/MonthYearPicker'

type FormFields = {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string
  is_current: boolean
  description: string
}

function toForm(item: ORExperience | null): FormFields {
  return {
    company: item?.company ?? '',
    title: item?.title ?? '',
    location: item?.location ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    is_current: item?.is_current ?? false,
    description: item?.description ?? '',
  }
}

function fromForm(form: FormFields): Omit<ORExperience, 'id' | 'resume_id' | 'display_order'> {
  return {
    company: form.company,
    title: form.title,
    location: form.location || null,
    start_date: form.start_date || null,
    end_date: form.is_current ? null : (form.end_date || null),
    is_current: !!form.is_current,
    description: form.description || null,
  }
}

interface Props {
  initial: ORExperience | null
  isSaving: boolean
  onSave: (data: Omit<ORExperience, 'id' | 'resume_id' | 'display_order'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function ORExperienceForm({ initial, isSaving, onSave, onCancel }: Props) {
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
            disabled={!!form.is_current}
          />
        </div>
      </div>

      <div className="flex items-center gap-2 mt-1">
        <input
          type="checkbox"
          id="is_current"
          checked={!!form.is_current}
          onChange={(e) => {
            const checked = e.target.checked
            setForm(f => ({ ...f, is_current: checked, end_date: checked ? '' : f.end_date }))
          }}
          className="w-4 h-4 text-sky-600 border-slate-300 rounded focus:ring-sky-500"
        />
        <label htmlFor="is_current" className="text-sm text-slate-600">I currently work here</label>
      </div>

      <div>
        <label className={labelClass}>Description</label>
        <textarea name="description" value={form.description} onChange={handleChange} rows={4} className={`${inputClass} resize-none`} />
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
