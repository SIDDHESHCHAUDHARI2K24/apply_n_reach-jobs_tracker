import React, { useState, useEffect } from 'react'
import { usePersonal } from './usePersonal'
import type { PersonalDetails } from '@features/user-profile/types'

type EditableFields = Omit<PersonalDetails, 'id' | 'profile_id' | 'created_at' | 'updated_at'>

const EMPTY: EditableFields = {
  full_name: '',
  email: '',
  phone: '',
  location: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  summary: '',
}

function toForm(data: PersonalDetails | null): EditableFields {
  if (!data) return EMPTY
  return {
    full_name: data.full_name ?? '',
    email: data.email ?? '',
    phone: data.phone ?? '',
    location: data.location ?? '',
    linkedin_url: data.linkedin_url ?? '',
    github_url: data.github_url ?? '',
    portfolio_url: data.portfolio_url ?? '',
    summary: data.summary ?? '',
  }
}

export function PersonalForm() {
  const { data, isLoading, isSaving, error, save } = usePersonal()
  const [form, setForm] = useState<EditableFields>(EMPTY)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    setForm(toForm(data))
  }, [data])

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
    setSuccess(false)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(false)
    try {
      const patch: Partial<EditableFields> = {}
      for (const key of Object.keys(form) as Array<keyof EditableFields>) {
        const val = form[key]
        patch[key] = val === '' ? null : val
      }
      await save(patch)
      setSuccess(true)
    } catch {
      // error is shown via hook state
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: '600px' }}>
      <h2>Personal Details</h2>
      {error && <div role="alert" style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>Saved successfully.</div>}

      <label>
        Full Name
        <input name="full_name" value={form.full_name ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Email
        <input name="email" type="email" value={form.email ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Phone
        <input name="phone" value={form.phone ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Location
        <input name="location" value={form.location ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        LinkedIn URL
        <input name="linkedin_url" value={form.linkedin_url ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        GitHub URL
        <input name="github_url" value={form.github_url ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Portfolio URL
        <input name="portfolio_url" value={form.portfolio_url ?? ''} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Summary
        <textarea name="summary" value={form.summary ?? ''} onChange={handleChange} rows={4} style={{ display: 'block', width: '100%' }} />
      </label>

      <button type="submit" disabled={isSaving}>
        {isSaving ? 'Saving...' : 'Save'}
      </button>
    </form>
  )
}
