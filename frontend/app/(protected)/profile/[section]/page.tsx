import { notFound } from 'next/navigation'
import PersonalPage from '../../../../src/app/profile/sections/PersonalPage'
import EducationPage from '../../../../src/app/profile/sections/EducationPage'
import ExperiencePage from '../../../../src/app/profile/sections/ExperiencePage'
import ProjectsPage from '../../../../src/app/profile/sections/ProjectsPage'
import ResearchPage from '../../../../src/app/profile/sections/ResearchPage'
import CertificationsPage from '../../../../src/app/profile/sections/CertificationsPage'
import SkillsPage from '../../../../src/app/profile/sections/SkillsPage'

interface PageProps {
  params: Promise<{ section: string }>
}

export default async function ProfileSectionRoutePage({ params }: PageProps) {
  const { section } = await params
  switch (section) {
    case 'personal':
      return <PersonalPage />
    case 'education':
      return <EducationPage />
    case 'experience':
      return <ExperiencePage />
    case 'projects':
      return <ProjectsPage />
    case 'research':
      return <ResearchPage />
    case 'certifications':
      return <CertificationsPage />
    case 'skills':
      return <SkillsPage />
    default:
      notFound()
  }
}
