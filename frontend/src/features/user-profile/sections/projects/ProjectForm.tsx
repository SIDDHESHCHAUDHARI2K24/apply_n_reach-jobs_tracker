import React, { useState } from 'react'
import type { Project } from '@features/user-profile/types'

type FormFields = {
  title: string
  description: string
  technologies: string
  url: string
  start_date: string
  end_date: string
  bullet_points: string
}

function toForm(item?: Project): FormFields {
  return {
    title: item?.title ?? '',
    description: item?.description ?? '',
    technologies: item?.technologies.join('\n') ?? '',
    url: item?.url ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    bullet_points: item?.bullet_points.join('\n') ?? '',
  }
}

function fromForm(form: FormFields): Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    title: form.title,
    description: form.description || null,
    technologies: form.technologies ? form.technologies.split('\n').filter(l => l.trim()) : [],
    url: form.url || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
  }
}

interface Props {
  initial?: Project
  isSaving: boolean
  onSave: (data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

export function ProjectForm({ initial, isSaving, onSave, onCancel }: Props) {
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
        Title *
        <input name="title" value={form.title} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Description
        <textarea name="description" value={form.description} onChange={handleChange} rows={3} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Technologies (one per line)
        <textarea name="technologies" value={form.technologies} onChange={handleChange} rows={3} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        URL
        <input name="url" value={form.url} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
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
