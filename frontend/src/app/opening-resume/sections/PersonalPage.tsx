'use client'

import React, { useState, useEffect } from 'react'
import { useORPersonal } from '@features/opening-resume/sections/useORPersonal'

const inputClass =
  'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
const labelClass = 'block text-sm font-medium text-slate-700 mb-1'

const emptyForm = {
  full_name: '',
  email: '',
  phone: '',
  location: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  summary: '',
}

export default function ORPersonalPage({ openingId }: { openingId: string }) {
  const { data, isLoading, isSaving, error, save } = useORPersonal(openingId)
  const [form, setForm] = useState(emptyForm)

  useEffect(() => {
    if (data) {
      setForm({
        full_name: data.full_name ?? '',
        email: data.email ?? '',
        phone: data.phone ?? '',
        location: data.location ?? '',
        linkedin_url: data.linkedin_url ?? '',
        github_url: data.github_url ?? '',
        portfolio_url: data.portfolio_url ?? '',
        summary: data.summary ?? '',
      })
    }
  }, [data])

  if (isLoading)
    return (
      <div className="flex items-center justify-center py-12 text-slate-400 text-sm">
        Loading...
      </div>
    )
  if (error)
    return (
      <div
        role="alert"
        className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm"
      >
        {error}
      </div>
    )

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    try {
      await save({
        full_name: form.full_name || null,
        email: form.email || null,
        phone: form.phone || null,
        location: form.location || null,
        linkedin_url: form.linkedin_url || null,
        github_url: form.github_url || null,
        portfolio_url: form.portfolio_url || null,
        summary: form.summary || null,
      })
    } catch {
      /* error shown by hook */
    }
  }

  return (
    <div className="max-w-2xl space-y-5">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">
          Personal Details
        </h3>
        <p className="text-xs text-slate-400 italic mt-0.5">
          Editing this snapshot does not affect your main profile.
        </p>
      </div>

      <form
        onSubmit={handleSave}
        className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>
              Full name <span className="text-red-400">*</span>
            </label>
            <input
              className={inputClass}
              value={form.full_name}
              required
              onChange={(e) =>
                setForm((f) => ({ ...f, full_name: e.target.value }))
              }
            />
          </div>
          <div>
            <label className={labelClass}>
              Email <span className="text-red-400">*</span>
            </label>
            <input
              type="email"
              className={inputClass}
              value={form.email}
              required
              onChange={(e) =>
                setForm((f) => ({ ...f, email: e.target.value }))
              }
            />
          </div>
          <div>
            <label className={labelClass}>Phone</label>
            <input
              type="tel"
              className={inputClass}
              value={form.phone}
              onChange={(e) =>
                setForm((f) => ({ ...f, phone: e.target.value }))
              }
            />
          </div>
          <div>
            <label className={labelClass}>Location</label>
            <input
              className={inputClass}
              value={form.location}
              onChange={(e) =>
                setForm((f) => ({ ...f, location: e.target.value }))
              }
            />
          </div>
          <div>
            <label className={labelClass}>LinkedIn URL</label>
            <input
              type="url"
              className={inputClass}
              value={form.linkedin_url}
              placeholder="https://linkedin.com/in/..."
              onChange={(e) =>
                setForm((f) => ({ ...f, linkedin_url: e.target.value }))
              }
            />
          </div>
          <div>
            <label className={labelClass}>GitHub URL</label>
            <input
              type="url"
              className={inputClass}
              value={form.github_url}
              placeholder="https://github.com/..."
              onChange={(e) =>
                setForm((f) => ({ ...f, github_url: e.target.value }))
              }
            />
          </div>
          <div className="sm:col-span-2">
            <label className={labelClass}>Portfolio URL</label>
            <input
              type="url"
              className={inputClass}
              value={form.portfolio_url}
              placeholder="https://..."
              onChange={(e) =>
                setForm((f) => ({ ...f, portfolio_url: e.target.value }))
              }
            />
          </div>
        </div>

        <div>
          <label className={labelClass}>Summary</label>
          <textarea
            rows={6}
            className={
              'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-y'
            }
            value={form.summary}
            onChange={(e) =>
              setForm((f) => ({ ...f, summary: e.target.value }))
            }
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  )
}
