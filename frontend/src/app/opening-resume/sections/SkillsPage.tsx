import React from 'react'
import { useParams } from 'react-router-dom'
import { useORSkills } from '@features/opening-resume/sections/useORSkills'

export default function ORSkillsPage() {
  const { openingId } = useParams<{ openingId: string }>()
  const { skills, isLoading, isSaving, error, replaceAll } = useORSkills(openingId ?? '')
  const [text, setTextState] = React.useState('')
  React.useEffect(() => { setTextState(skills.join('\n')) }, [skills])

  if (isLoading) return <div>Loading...</div>
  if (error) return <div role="alert">{error}</div>

  return (
    <div>
      <h3>Skills (Snapshot)</h3>
      <textarea rows={8} value={text} onChange={e => setTextState(e.target.value)} style={{ width: '100%' }} />
      <button onClick={() => replaceAll(text.split('\n').map(s => s.trim()).filter(Boolean))} disabled={isSaving}>
        {isSaving ? 'Saving...' : 'Save Skills'}
      </button>
    </div>
  )
}
