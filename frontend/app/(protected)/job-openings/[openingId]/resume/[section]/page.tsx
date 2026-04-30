import { notFound } from 'next/navigation'
import ORPersonalPage from '../../../../../../src/app/opening-resume/sections/PersonalPage'
import OREducationPage from '../../../../../../src/app/opening-resume/sections/EducationPage'
import ORExperiencePage from '../../../../../../src/app/opening-resume/sections/ExperiencePage'
import ORProjectsPage from '../../../../../../src/app/opening-resume/sections/ProjectsPage'
import ORResearchPage from '../../../../../../src/app/opening-resume/sections/ResearchPage'
import ORCertificationsPage from '../../../../../../src/app/opening-resume/sections/CertificationsPage'
import ORSkillsPage from '../../../../../../src/app/opening-resume/sections/SkillsPage'

interface PageProps {
  params: Promise<{ openingId: string; section: string }>
}

export default async function OpeningResumeSectionRoutePage({ params }: PageProps) {
  const { openingId, section } = await params

  switch (section) {
    case 'personal':
      return <ORPersonalPage openingId={openingId} />
    case 'education':
      return <OREducationPage openingId={openingId} />
    case 'experience':
      return <ORExperiencePage openingId={openingId} />
    case 'projects':
      return <ORProjectsPage openingId={openingId} />
    case 'research':
      return <ORResearchPage openingId={openingId} />
    case 'certifications':
      return <ORCertificationsPage openingId={openingId} />
    case 'skills':
      return <ORSkillsPage openingId={openingId} />
    default:
      notFound()
  }
}
