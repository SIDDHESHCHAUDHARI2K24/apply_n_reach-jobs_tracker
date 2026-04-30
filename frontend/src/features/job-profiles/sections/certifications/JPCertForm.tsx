import React, { useState } from 'react'
import { Globe } from 'lucide-react'
import type { JPCertification } from '@features/job-profiles/types'

type FormFields = {
  name: string
  credential_url: string
}

function toForm(item: JPCertification | null): FormFields {
  return {
    name: item?.name ?? '',
    credential_url: item?.credential_url ?? '',
  }
}

function fromForm(form: FormFields): Omit<JPCertification, 'id' | 'job_profile_id'> {
  return {
    name: form.name,
    issuing_organization: null,
    issue_date: null,
    expiry_date: null,
    credential_id: null,
    credential_url: form.credential_url || null,
  }
}

interface Props {
  initial: JPCertification | null
  isSaving: boolean
  onSave: (data: Omit<JPCertification, 'id' | 'job_profile_id'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700'

export function JPCertForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      <div className="space-y-1">
        <label className={labelClass}>Certificate Name <span className="text-red-500">*</span></label>
        <input
          name="name"
          value={form.name}
          onChange={handleChange}
          required
          placeholder="e.g. AWS Certified Solutions Architect"
          className={inputClass}
        />
      </div>

      <div className="space-y-1">
        <label className={labelClass}>Verification URL</label>
        <div className="relative">
          <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            name="credential_url"
            value={form.credential_url}
            onChange={handleChange}
            placeholder="https://..."
            className={`${inputClass} pl-9`}
          />
        </div>
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
