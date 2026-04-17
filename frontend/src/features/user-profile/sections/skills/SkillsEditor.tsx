import React, { useState, useEffect } from 'react'
import { useSkills } from './useSkills'

export function SkillsEditor() {
  const { skills, isLoading, isSaving, error, replaceAll } = useSkills()
  const [text, setText] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    setText(skills.join('\n'))
  }, [skills])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(false)
    const newSkills = text.split('\n').map(s => s.trim()).filter(Boolean)
    try {
      await replaceAll(newSkills)
      setSuccess(true)
    } catch {
      // error shown via hook state
    }
  }

  if (isLoading) return <div>Loading skills...</div>

  return (
    <div>
      <h2>Skills</h2>
      {error && <div role="alert" style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>Skills saved successfully.</div>}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: '400px' }}>
        <label>
          Skills (one per line)
          <textarea
            value={text}
            onChange={e => { setText(e.target.value); setSuccess(false) }}
            rows={10}
            style={{ display: 'block', width: '100%' }}
          />
        </label>
        <button type="submit" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save Skills'}
        </button>
      </form>
    </div>
  )
}
