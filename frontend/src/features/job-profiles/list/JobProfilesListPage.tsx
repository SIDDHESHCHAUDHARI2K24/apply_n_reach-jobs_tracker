'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Plus, FolderOpen, Trash2, AlertCircle } from 'lucide-react'
import { useJobProfiles } from './useJobProfiles'
import type { JobProfileStatus } from '@features/job-profiles/types'

const STATUS_FILTERS: Array<{ label: string; value: JobProfileStatus | 'all' }> = [
  { label: 'All', value: 'all' },
  { label: 'Draft', value: 'draft' },
  { label: 'Active', value: 'active' },
  { label: 'Archived', value: 'archived' },
]

export function JobProfilesListPage() {
  const { profiles, isLoading, isSaving, error, statusFilter, hasMore, setFilter, loadMore, create, remove, activate, archive } = useJobProfiles()
  const [showCreate, setShowCreate] = useState(false)
  const [newTitle, setNewTitle] = useState('')

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newTitle.trim()) return
    try {
      await create({ title: newTitle.trim() })
      setNewTitle('')
      setShowCreate(false)
    } catch {
      // error shown by hook
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl" style={{ fontFamily: 'var(--font-heading)' }}>Job Profiles</h1>
        <button
          onClick={() => setShowCreate(s => !s)}
          className="flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Plus size={16} />
          New Profile
        </button>
      </div>

      {/* Create form panel */}
      {showCreate && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl shadow-sm p-5 mb-6">
          <h2 className="text-base font-semibold text-slate-800 mb-3">Create New Profile</h2>
          <form onSubmit={handleCreate} className="flex gap-3">
            <input
              value={newTitle}
              onChange={e => setNewTitle(e.target.value)}
              placeholder="Profile title (e.g. Senior Engineer at Google)"
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              autoFocus
            />
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {isSaving ? 'Creating…' : 'Create'}
            </button>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-600 text-sm font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Status filter pills */}
      <div className="flex gap-2 mb-6">
        {STATUS_FILTERS.map(f => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              statusFilter === f.value
                ? 'bg-sky-500 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div role="alert" className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-6">
          <AlertCircle size={16} className="shrink-0" />
          {error}
        </div>
      )}

      {/* Loading state */}
      {isLoading && profiles.length === 0 && (
        <div className="text-sm text-slate-400 py-8 text-center">Loading...</div>
      )}

      {/* Empty state */}
      {!isLoading && profiles.length === 0 && !error && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <FolderOpen size={48} className="text-slate-300 mb-4" />
          <p className="text-slate-500 font-medium mb-1">No profiles yet</p>
          <p className="text-slate-400 text-sm mb-4">Create a job profile to tailor your resume for specific roles.</p>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <Plus size={16} />
            New Profile
          </button>
        </div>
      )}

      {/* Profile grid */}
      {profiles.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {profiles.map(profile => (
            <div
              key={profile.id}
              className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex flex-col gap-3"
            >
              {/* Card body */}
              <div className="flex-1">
                <div className="font-semibold text-slate-900 mb-2 leading-snug" style={{ fontFamily: 'var(--font-heading)' }}>
                  {profile.title}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge badge-${profile.status}`}>{profile.status}</span>
                  <span className="text-xs text-slate-400">
                    Created {new Date(profile.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
              </div>

              {/* Card footer */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2">
                  <Link
                    href={`/job-profiles/${profile.id}/edit`}
                    className="text-sm font-medium text-sky-500 hover:text-sky-600 transition-colors"
                  >
                    Edit
                  </Link>
                  {profile.status === 'active' ? (
                    <button
                      onClick={() => { archive(profile.id).catch(() => {}) }}
                      disabled={isSaving}
                      className="px-2 py-1 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 hover:bg-amber-100 rounded-md transition-colors disabled:opacity-50"
                    >
                      Archive
                    </button>
                  ) : (
                    <button
                      onClick={() => { activate(profile.id).catch(() => {}) }}
                      disabled={isSaving}
                      className="px-2 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded-md transition-colors disabled:opacity-50"
                    >
                      Activate
                    </button>
                  )}
                </div>
                <button
                  onClick={() => { remove(profile.id).catch(() => {}) }}
                  disabled={isSaving}
                  className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
                  aria-label="Delete profile"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Load more */}
      {hasMore && (
        <div className="mt-6 text-center">
          <button
            onClick={loadMore}
            disabled={isLoading}
            className="px-5 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-600 text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Loading…' : 'Load more'}
          </button>
        </div>
      )}
    </div>
  )
}
