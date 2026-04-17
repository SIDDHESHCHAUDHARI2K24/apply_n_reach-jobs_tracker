import React, { useState } from 'react'
import type { Education } from '@features/user-profile/types'

type FormFields = {
  institution: string
  degree: string
  field_of_study: string
  start_date: string
  end_date: string
  gpa: string
  bullet_points: string
}

function toForm(item?: Education): FormFields {
  return {
    institution: item?.institution ?? '',
    degree: item?.degree ?? '',
    field_of_study: item?.field_of_study ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    gpa: item?.gpa ?? '',
    bullet_points: item?.bullet_points.join('\n') ?? '',
  }
}

function fromForm(form: FormFields): Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    institution: form.institution,
    degree: form.degree,
    field_of_study: form.field_of_study || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    gpa: form.gpa || null,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
  }
}

interface Props {
  initial?: Education
  isSaving: boolean
  onSave: (data: Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function EducationForm({ initial, isSaving, onSave, onCancel }: Props) {
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
          <label className={labelClass}>Institution *</label>
          <input name="institution" value={form.institution} onChange={handleChange} required className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Degree *</label>
          <input name="degree" value={form.degree} onChange={handleChange} required className={inputClass} />
        </div>
      </div>

      <div>
        <label className={labelClass}>Field of Study</label>
        <input name="field_of_study" value={form.field_of_study} onChange={handleChange} className={inputClass} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Start Date</label>
          <input name="start_date" value={form.start_date} onChange={handleChange} placeholder="YYYY-MM-DD" className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>End Date</label>
          <input name="end_date" value={form.end_date} onChange={handleChange} placeholder="YYYY-MM-DD" className={inputClass} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>GPA</label>
          <input name="gpa" value={form.gpa} onChange={handleChange} className={inputClass} />
        </div>
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
