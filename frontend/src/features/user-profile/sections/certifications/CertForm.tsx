import React, { useState } from 'react'
import type { Certification } from '@features/user-profile/types'

type FormFields = {
  name: string
  issuing_organization: string
  issue_date: string
  expiry_date: string
  credential_id: string
  credential_url: string
}

function toForm(item?: Certification): FormFields {
  return {
    name: item?.name ?? '',
    issuing_organization: item?.issuing_organization ?? '',
    issue_date: item?.issue_date ?? '',
    expiry_date: item?.expiry_date ?? '',
    credential_id: item?.credential_id ?? '',
    credential_url: item?.credential_url ?? '',
  }
}

function fromForm(form: FormFields): Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    name: form.name,
    issuing_organization: form.issuing_organization || null,
    issue_date: form.issue_date || null,
    expiry_date: form.expiry_date || null,
    credential_id: form.credential_id || null,
    credential_url: form.credential_url || null,
  }
}

interface Props {
  initial?: Certification
  isSaving: boolean
  onSave: (data: Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

export function CertForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '500px' }}>
      <label>
        Name *
        <input name="name" value={form.name} onChange={handleChange} required style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Issuing Organization
        <input name="issuing_organization" value={form.issuing_organization} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Issue Date
        <input name="issue_date" value={form.issue_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Expiry Date
        <input name="expiry_date" value={form.expiry_date} onChange={handleChange} placeholder="YYYY-MM-DD" style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Credential ID
        <input name="credential_id" value={form.credential_id} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <label>
        Credential URL
        <input name="credential_url" value={form.credential_url} onChange={handleChange} style={{ display: 'block', width: '100%' }} />
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit" disabled={isSaving}>{isSaving ? 'Saving...' : 'Save'}</button>
        <button type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}
