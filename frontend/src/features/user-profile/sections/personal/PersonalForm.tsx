import React, { useState, useEffect } from 'react'
import { usePersonal } from './usePersonal'
import type { PersonalDetails } from '@features/user-profile/types'
import { Link2, Globe, AlertCircle } from 'lucide-react'

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

  useEffect(() => {
    if (success) {
      const t = setTimeout(() => setSuccess(false), 2000)
      return () => clearTimeout(t)
    }
  }, [success])

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

  if (isLoading) return (
    <div className="text-sm text-slate-500 py-8">Loading...</div>
  )

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="font-['Sora'] text-xl font-semibold text-slate-800">Personal Details</h2>

      {error && (
        <div role="alert" className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Full Name</label>
          <input
            name="full_name"
            value={form.full_name ?? ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            name="email"
            type="email"
            value={form.email ?? ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Phone</label>
          <input
            name="phone"
            value={form.phone ?? ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Location</label>
          <input
            name="location"
            value={form.location ?? ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="space-y-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">LinkedIn URL</label>
          <div className="relative">
            <Link2 className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              name="linkedin_url"
              value={form.linkedin_url ?? ''}
              onChange={handleChange}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              placeholder="https://linkedin.com/in/yourprofile"
            />
          </div>
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">GitHub URL</label>
          <div className="relative">
            <Link2 className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              name="github_url"
              value={form.github_url ?? ''}
              onChange={handleChange}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              placeholder="https://github.com/yourusername"
            />
          </div>
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Portfolio URL</label>
          <div className="relative">
            <Globe className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              name="portfolio_url"
              value={form.portfolio_url ?? ''}
              onChange={handleChange}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              placeholder="https://yourportfolio.com"
            />
          </div>
        </div>
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-medium text-slate-700">Summary</label>
        <textarea
          name="summary"
          value={form.summary ?? ''}
          onChange={handleChange}
          rows={4}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
        />
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={isSaving}
          className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
        {success && (
          <span className="text-green-600 text-sm font-medium">&#10003; Saved</span>
        )}
      </div>
    </form>
  )
}
