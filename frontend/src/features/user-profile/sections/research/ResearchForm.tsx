import React, { useState } from 'react'
import type { Research } from '@features/user-profile/types'

type FormFields = {
  title: string
  institution: string
  journal: string
  year: string
  description: string
  url: string
  bullet_points: string
  reference_links: string
}

function toForm(item?: Research): FormFields {
  return {
    title: item?.title ?? '',
    institution: item?.institution ?? '',
    journal: item?.journal ?? '',
    year: item?.year ?? '',
    description: item?.description ?? '',
    url: item?.url ?? '',
    bullet_points: item?.bullet_points.join('\n') ?? '',
    reference_links: item?.reference_links.join('\n') ?? '',
  }
}

function fromForm(form: FormFields): Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    title: form.title,
    institution: form.institution || null,
    journal: form.journal || null,
    year: form.year || null,
    description: form.description || null,
    url: form.url || null,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
    reference_links: form.reference_links ? form.reference_links.split('\n').filter(l => l.trim()) : [],
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

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '500px' }}>
      <label>
        Title *
        <input name="title" value={form.title} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Institution
        <input name="institution" value={form.institution} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Journal
        <input name="journal" value={form.journal} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Year
        <input name="year" value={form.year} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Description
        <textarea name="description" value={form.description} onChange={handleChange} rows={3} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        URL
        <input name="url" value={form.url} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Bullet Points (one per line)
        <textarea name="bullet_points" value={form.bullet_points} onChange={handleChange} rows={4} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Reference Links (one per line)
        <textarea name="reference_links" value={form.reference_links} onChange={handleChange} rows={3} style={{ display: 'block', width: '100%' }} />
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit" disabled={isSaving}>{isSaving ? 'Saving...' : 'Save'}</button>
        <button type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}
