import React, { useState } from 'react'
import { Globe } from 'lucide-react'
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

  const fieldClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
  const labelClass = 'block text-sm font-medium text-slate-700'

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      {/* Name */}
      <div className="space-y-1">
        <label className={labelClass}>Certificate Name <span className="text-red-500">*</span></label>
        <input
          name="name"
          value={form.name}
          onChange={handleChange}
          required
          placeholder="e.g. AWS Certified Solutions Architect"
          className={fieldClass}
        />
      </div>

      {/* Issuing Organization + Credential ID */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className={labelClass}>Issuing Organization</label>
          <input
            name="issuing_organization"
            value={form.issuing_organization}
            onChange={handleChange}
            placeholder="e.g. Amazon Web Services"
            className={fieldClass}
          />
        </div>
        <div className="space-y-1">
          <label className={labelClass}>Credential ID</label>
          <input
            name="credential_id"
            value={form.credential_id}
            onChange={handleChange}
            placeholder="e.g. ABC123XYZ"
            className={fieldClass}
          />
        </div>
      </div>

      {/* Issue Date + Expiry Date */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className={labelClass}>Issue Date</label>
          <input
            name="issue_date"
            value={form.issue_date}
            onChange={handleChange}
            placeholder="YYYY-MM-DD"
            className={fieldClass}
          />
        </div>
        <div className="space-y-1">
          <label className={labelClass}>Expiry Date</label>
          <input
            name="expiry_date"
            value={form.expiry_date}
            onChange={handleChange}
            placeholder="YYYY-MM-DD or leave blank"
            className={fieldClass}
          />
        </div>
      </div>

      {/* Credential URL */}
      <div className="space-y-1">
        <label className={labelClass}>Credential URL</label>
        <div className="relative">
          <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            name="credential_url"
            value={form.credential_url}
            onChange={handleChange}
            placeholder="https://..."
            className={`${fieldClass} pl-9`}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 pt-1">
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
