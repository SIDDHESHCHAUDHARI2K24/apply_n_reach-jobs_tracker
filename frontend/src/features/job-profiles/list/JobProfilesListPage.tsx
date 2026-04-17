import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useJobProfiles } from './useJobProfiles'
import type { JobProfileStatus } from '@features/job-profiles/types'

const STATUS_FILTERS: Array<{ label: string; value: JobProfileStatus | 'all' }> = [
  { label: 'All', value: 'all' },
  { label: 'Draft', value: 'draft' },
  { label: 'Active', value: 'active' },
  { label: 'Archived', value: 'archived' },
]

export function JobProfilesListPage() {
  const { profiles, isLoading, isSaving, error, statusFilter, hasMore, setFilter, loadMore, create, remove } = useJobProfiles()
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
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1>Job Profiles</h1>
        <button onClick={() => setShowCreate(s => !s)}>+ New Profile</button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
          <input
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            placeholder="Profile title (e.g. Senior Engineer at Google)"
            style={{ flex: 1 }}
            autoFocus
          />
          <button type="submit" disabled={isSaving}>Create</button>
          <button type="button" onClick={() => setShowCreate(false)}>Cancel</button>
        </form>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {STATUS_FILTERS.map(f => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            style={{ fontWeight: statusFilter === f.value ? 700 : 400 }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && <div role="alert" style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

      {isLoading && profiles.length === 0 && <div>Loading...</div>}

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {profiles.map(profile => (
          <li key={profile.id} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 600 }}>{profile.title}</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                {profile.status} · {new Date(profile.created_at).toLocaleDateString()}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Link to={`/job-profiles/${profile.id}/edit`}>Edit</Link>
              <button onClick={() => { remove(profile.id).catch(() => {}) }} disabled={isSaving}>Delete</button>
            </div>
          </li>
        ))}
      </ul>

      {hasMore && (
        <button onClick={loadMore} disabled={isLoading}>Load more</button>
      )}
    </div>
  )
}
