'use client'

import React, { useState } from 'react'
import { Globe } from 'lucide-react'
import { MonthYearPicker } from '../../../components/MonthYearPicker'
import type { ORCertification } from '@features/opening-resume/types'

type FormFields = {
  name: string
  issuing_organization: string
  issue_date: string
  expiry_date: string
  credential_id: string
  credential_url: string
}

function toForm(item: ORCertification | null): FormFields {
  return {
    name: item?.name ?? '',
    issuing_organization: item?.issuing_organization ?? '',
    issue_date: item?.issue_date ?? '',
    expiry_date: item?.expiry_date ?? '',
    credential_id: item?.credential_id ?? '',
    credential_url: item?.credential_url ?? '',
  }
}

function fromForm(form: FormFields): Omit<ORCertification, 'id' | 'resume_id'> {
  return {
    name: form.name.trim(),
    issuing_organization: form.issuing_organization.trim() || null,
    issue_date: form.issue_date || null,
    expiry_date: form.expiry_date || null,
    credential_id: form.credential_id.trim() || null,
    credential_url: form.credential_url.trim() || null,
    display_order: 0,
  }
}

interface Props {
  initial: ORCertification | null
  isSaving: boolean
  onSave: (data: Omit<ORCertification, 'id' | 'resume_id'>) => Promise<void>
  onCancel: () => void
}

const inputClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

export function ORCertificationForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name.trim()) return
    await onSave(fromForm(form))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      <div>
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

      <div>
        <label className={labelClass}>Issuing Organization</label>
        <input
          name="issuing_organization"
          value={form.issuing_organization}
          onChange={handleChange}
          placeholder="e.g. Amazon Web Services"
          className={inputClass}
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Issue Date</label>
          <MonthYearPicker
            value={form.issue_date}
            onChange={(v: string) => setForm(f => ({ ...f, issue_date: v }))}
            placeholder="Month"
          />
        </div>
        <div>
          <label className={labelClass}>Expiry Date</label>
          <MonthYearPicker
            value={form.expiry_date}
            onChange={(v: string) => setForm(f => ({ ...f, expiry_date: v }))}
            placeholder="Month"
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Credential ID</label>
        <input
          name="credential_id"
          value={form.credential_id}
          onChange={handleChange}
          placeholder="e.g. ABC123XYZ"
          className={inputClass}
        />
      </div>

      <div>
        <label className={labelClass}>Credential URL</label>
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
