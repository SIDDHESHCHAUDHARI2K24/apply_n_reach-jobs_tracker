import { useParams, useSearchParams, Link } from 'react-router-dom'
import { RenderPanel } from '@features/job-profiles/render/RenderPanel'
import { JPSectionContent } from './JPSectionContent'

const SECTIONS = [
  { label: 'Personal', key: 'personal' },
  { label: 'Education', key: 'education' },
  { label: 'Experience', key: 'experience' },
  { label: 'Projects', key: 'projects' },
  { label: 'Research', key: 'research' },
  { label: 'Certifications', key: 'certifications' },
  { label: 'Skills', key: 'skills' },
]

export function JobProfileEditor() {
  const { jobProfileId } = useParams<{ jobProfileId: string }>()
  const [searchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') ?? 'personal'

  if (!jobProfileId) return <div>Invalid profile ID</div>

  return (
    <div style={{ display: 'flex', gap: '1rem', height: 'calc(100vh - 120px)' }}>
      {/* Left tab rail */}
      <div style={{ width: 160, borderRight: '1px solid #e5e7eb' }}>
        <nav>
          {SECTIONS.map(s => (
            <div key={s.key}>
              <Link
                to={`/job-profiles/${jobProfileId}/edit?tab=${s.key}`}
                style={{
                  display: 'block',
                  padding: '0.5rem',
                  fontWeight: activeTab === s.key ? 700 : 400,
                  textDecoration: 'none',
                  background: activeTab === s.key ? '#f5f3ff' : 'transparent',
                }}
              >
                {s.label}
              </Link>
            </div>
          ))}
        </nav>
      </div>

      {/* Main editor area */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '1rem' }}>
          Editing section: <strong>{activeTab}</strong>
        </p>
        <JPSectionContent jobProfileId={jobProfileId} section={activeTab} />
      </div>

      {/* Right render panel */}
      <div style={{ width: 280 }}>
        <RenderPanel jobProfileId={jobProfileId} />
      </div>
    </div>
  )
}
