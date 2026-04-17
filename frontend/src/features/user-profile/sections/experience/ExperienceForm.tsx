import React, { useState } from 'react'
import type { Experience } from '@features/user-profile/types'

type FormFields = {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string
  is_current: boolean
  bullet_points: string
}

function toForm(item?: Experience): FormFields {
  return {
    company: item?.company ?? '',
    title: item?.title ?? '',
    location: item?.location ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    is_current: item?.is_current ?? false,
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
    is_current: form.is_current,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
  }
}

interface Props {
  initial?: Experience
  isSaving: boolean
  onSave: (data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

export function ExperienceForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value, type } = e.target
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '500px' }}>
      <label>
        Company *
        <input name="company" value={form.company} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Title *
        <input name="title" value={form.title} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Location
        <input name="location" value={form.location} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Start Date
        <input name="start_date" value={form.start_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        End Date
        <input name="end_date" value={form.end_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <input name="is_current" type="checkbox" checked={form.is_current} onChange={handleChange} />
        Currently working here
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
