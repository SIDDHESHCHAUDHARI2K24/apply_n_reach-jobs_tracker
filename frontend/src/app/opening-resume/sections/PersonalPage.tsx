'use client'

import React, { useState, useEffect } from 'react'
import { useORPersonal } from '@features/opening-resume/sections/useORPersonal'

export default function ORPersonalPage({ openingId }: { openingId: string }) {
  const { data, isLoading, isSaving, error, save } = useORPersonal(openingId)
  const [form, setForm] = useState({ full_name: '', email: '', summary: '' })

  // Sync form with loaded data
  useEffect(() => {
    if (data) {
      setForm({ full_name: data.full_name ?? '', email: data.email ?? '', summary: data.summary ?? '' })
    }
  }, [data])

  if (isLoading) return (
    <div className="flex items-center justify-center py-12 text-slate-400 text-sm">Loading...</div>
  )
  if (error) return (
    <div role="alert" className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
  )

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    try {
      await save({ full_name: form.full_name || null, email: form.email || null, summary: form.summary || null })
    } catch { /* error shown by hook */ }
  }

  return (
    <div className="max-w-2xl space-y-5">
      <div>
        <h3 className="font-sora text-base font-semibold text-slate-800">Personal Details</h3>
        <p className="text-xs text-slate-400 italic mt-0.5">Editing this snapshot does not affect your main profile.</p>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Full name</label>
          <input
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.full_name}
            onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Summary</label>
          <textarea
            rows={4}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-y"
            value={form.summary}
            onChange={e => setForm(f => ({ ...f, summary: e.target.value }))}
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
