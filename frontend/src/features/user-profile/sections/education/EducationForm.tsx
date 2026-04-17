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
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '500px' }}>
      <label>
        Institution *
        <input name="institution" value={form.institution} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Degree *
        <input name="degree" value={form.degree} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Field of Study
        <input name="field_of_study" value={form.field_of_study} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Start Date
        <input name="start_date" value={form.start_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        End Date
        <input name="end_date" value={form.end_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        GPA
        <input name="gpa" value={form.gpa} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Bullet Points (one per line)
        <textarea name="bullet_points" value={form.bullet_points} onChange={handleChange} rows={4} style={{ display: 'block', width: '100%' }} />
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit" disabled={isSaving}>{isSaving ? 'Saving...' : 'Save'}</button>
        <button type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}
