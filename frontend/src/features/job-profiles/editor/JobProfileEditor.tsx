'use client'

import Link from 'next/link'
import { useParams, useSearchParams } from 'next/navigation'
import { RenderPanel } from '@features/job-profiles/render/RenderPanel'
import { JPSectionContent } from './JPSectionContent'
import { JPEducationList } from '@features/job-profiles/sections/education/JPEducationList'
import { JPExperienceList } from '@features/job-profiles/sections/experience/JPExperienceList'
import { JPProjectList } from '@features/job-profiles/sections/projects/JPProjectList'
import { JPResearchList } from '@features/job-profiles/sections/research/JPResearchList'
import { JPCertList } from '@features/job-profiles/sections/certifications/JPCertList'
import { JPSkillsEditor } from '@features/job-profiles/sections/skills/JPSkillsEditor'

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
  const params = useParams<{ jobProfileId?: string }>()
  const searchParams = useSearchParams()
  const jobProfileId = params?.jobProfileId
  const activeTab = searchParams.get('tab') ?? 'personal'

  if (!jobProfileId) return <div className="p-6 text-red-500">Invalid profile ID</div>

  return (
    <div className="flex gap-0 h-[calc(100vh-64px)] overflow-hidden">
      {/* Left tab rail */}
      <nav className="w-40 shrink-0 bg-white border-r border-slate-200 flex flex-col py-3 overflow-y-auto">
        <p className="px-4 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Sections</p>
        {SECTIONS.map(s => (
          <Link
            key={s.key}
            href={`/job-profiles/${jobProfileId}/edit?tab=${s.key}`}
            className={`relative flex items-center px-4 py-2.5 text-sm font-medium transition-colors no-underline ${
              activeTab === s.key
                ? 'text-sky-600 bg-sky-50 border-l-2 border-sky-500'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 border-l-2 border-transparent'
            }`}
          >
            {s.label}
          </Link>
        ))}
      </nav>

      {/* Main editor area */}
      <div className="flex-1 overflow-y-auto bg-slate-50 p-6">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg mb-4 capitalize" style={{ fontFamily: 'var(--font-heading)' }}>
            {activeTab}
          </h2>
          {activeTab === 'personal' && <JPSectionContent jobProfileId={jobProfileId} section="personal" />}
          {activeTab === 'education' && <JPEducationList jobProfileId={jobProfileId} />}
          {activeTab === 'experience' && <JPExperienceList jobProfileId={jobProfileId} />}
          {activeTab === 'projects' && <JPProjectList jobProfileId={jobProfileId} />}
          {activeTab === 'research' && <JPResearchList jobProfileId={jobProfileId} />}
          {activeTab === 'certifications' && <JPCertList jobProfileId={jobProfileId} />}
          {activeTab === 'skills' && <JPSkillsEditor jobProfileId={jobProfileId} />}
        </div>
      </div>

      {/* Right render panel */}
      <div className="w-[300px] shrink-0 overflow-y-auto bg-white border-l border-slate-200 p-4">
        <RenderPanel jobProfileId={jobProfileId} />
      </div>
    </div>
  )
}
