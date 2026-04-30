import { apiRequest } from '@core/http/client'
import type {
  OpeningResume,
  ORCertification,
  OREducation,
  ORExperience,
  ORPersonal,
  ORProject,
  ORResearch,
  ORSkillItem,
} from './types'
import type {
  OpeningResumeCertificationResponse,
  OpeningResumeEducationResponse,
  OpeningResumeExperienceResponse,
  OpeningResumePersonalResponse,
  OpeningResumeProjectResponse,
  OpeningResumeResearchResponse,
  OpeningResumeResponse,
  OpeningResumeSkillResponse,
} from '@generated/contracts'

const base = (openingId: string) => `/job-openings/${openingId}/resume`
const asId = (id: number) => String(id)

const mapResume = (row: OpeningResumeResponse): OpeningResume => ({
  id: asId(row.id),
  job_opening_id: asId(row.opening_id),
  source_job_profile_id: row.source_job_profile_id != null ? asId(row.source_job_profile_id) : null,
  status: row.status,
  generated_at: row.generated_at ?? null,
})

const mapPersonal = (row: OpeningResumePersonalResponse): ORPersonal => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  full_name: row.full_name ?? null,
  email: row.email ?? null,
  phone: row.phone ?? null,
  location: row.location ?? null,
  linkedin_url: row.linkedin_url ?? null,
  github_url: row.github_url ?? null,
  portfolio_url: row.portfolio_url ?? null,
  summary: row.summary ?? null,
  updated_at: '',
})

const mapEducation = (row: OpeningResumeEducationResponse): OREducation => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  institution: row.institution,
  degree: row.degree ?? null,
  field_of_study: row.field_of_study ?? null,
  start_date: row.start_date ?? null,
  end_date: row.end_date ?? null,
  gpa: row.grade ?? null,
  description: row.description ?? null,
  display_order: row.display_order,
})

const mapExperience = (row: OpeningResumeExperienceResponse): ORExperience => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  company: row.company,
  title: row.title,
  location: row.location ?? null,
  start_date: row.start_date ?? null,
  end_date: row.end_date ?? null,
  is_current: row.is_current,
  description: row.description ?? null,
  display_order: row.display_order,
})

const mapProject = (row: OpeningResumeProjectResponse): ORProject => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  title: row.name,
  description: row.description ?? null,
  technologies: row.technologies ?? [],
  url: row.url ?? null,
  start_date: row.start_date ?? null,
  end_date: row.end_date ?? null,
  display_order: row.display_order,
})

const mapResearch = (row: OpeningResumeResearchResponse): ORResearch => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  title: row.title,
  publication: row.publication ?? null,
  published_date: row.published_date ?? null,
  description: row.description ?? null,
  url: row.url ?? null,
  display_order: row.display_order,
})

const mapCertification = (row: OpeningResumeCertificationResponse): ORCertification => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  name: row.name,
  issuing_organization: row.issuer ?? null,
  issue_date: row.issue_date ?? null,
  expiry_date: row.expiry_date ?? null,
  credential_id: row.credential_id ?? null,
  credential_url: row.url ?? null,
  display_order: row.display_order,
})

const mapSkill = (row: OpeningResumeSkillResponse): ORSkillItem => ({
  id: asId(row.id),
  resume_id: asId(row.resume_id),
  category: row.category,
  name: row.name,
  proficiency_level: row.proficiency_level ?? null,
  display_order: row.display_order,
})

export const openingResumeApi = {
  create: (openingId: string, sourceJobProfileId?: string) => {
    const params = new URLSearchParams()
    if (sourceJobProfileId) {
      params.set('source_job_profile_id', sourceJobProfileId)
    }
    const suffix = params.toString()
    return apiRequest<OpeningResumeResponse>(`${base(openingId)}${suffix ? `?${suffix}` : ''}`, { method: 'POST' }).then(mapResume)
  },
  get: (openingId: string) =>
    apiRequest<OpeningResumeResponse>(`${base(openingId)}`).then(mapResume),

  // Personal (PUT)
  getPersonal: (openingId: string) => apiRequest<OpeningResumePersonalResponse>(`${base(openingId)}/personal`).then(mapPersonal),
  updatePersonal: (openingId: string, data: Partial<ORPersonal>) =>
    apiRequest<OpeningResumePersonalResponse>(`${base(openingId)}/personal`, {
      method: 'PUT',
      body: {
        full_name: data.full_name ?? undefined,
        email: data.email ?? undefined,
        phone: data.phone ?? undefined,
        location: data.location ?? undefined,
        linkedin_url: data.linkedin_url ?? undefined,
        github_url: data.github_url ?? undefined,
        portfolio_url: data.portfolio_url ?? undefined,
        summary: data.summary ?? undefined,
      },
    }).then(mapPersonal),

  // Education
  getEducation: (openingId: string) => apiRequest<OpeningResumeEducationResponse[]>(`${base(openingId)}/education`).then(rows => rows.map(mapEducation)),
  createEducation: (openingId: string, data: Omit<OREducation, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeEducationResponse>(`${base(openingId)}/education`, {
      method: 'POST',
      body: {
        institution: data.institution,
        degree: data.degree ?? null,
        field_of_study: data.field_of_study ?? null,
        start_date: data.start_date ?? null,
        end_date: data.end_date ?? null,
        grade: data.gpa ?? null,
        description: data.description ?? null,
        display_order: data.display_order ?? 0,
      },
    }).then(mapEducation),
  updateEducation: (openingId: string, itemId: string, data: Partial<Omit<OREducation, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeEducationResponse>(`${base(openingId)}/education/${itemId}`, {
      method: 'PATCH',
      body: {
        institution: data.institution ?? undefined,
        degree: data.degree ?? undefined,
        field_of_study: data.field_of_study ?? undefined,
        start_date: data.start_date ?? undefined,
        end_date: data.end_date ?? undefined,
        grade: data.gpa ?? undefined,
        description: data.description ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapEducation),
  deleteEducation: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/education/${itemId}`, { method: 'DELETE' }),

  // Experience
  getExperience: (openingId: string) => apiRequest<OpeningResumeExperienceResponse[]>(`${base(openingId)}/experience`).then(rows => rows.map(mapExperience)),
  createExperience: (openingId: string, data: Omit<ORExperience, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeExperienceResponse>(`${base(openingId)}/experience`, {
      method: 'POST',
      body: {
        company: data.company,
        title: data.title,
        location: data.location ?? null,
        start_date: data.start_date ?? null,
        end_date: data.end_date ?? null,
        is_current: data.is_current,
        description: data.description ?? null,
        display_order: data.display_order ?? 0,
      },
    }).then(mapExperience),
  updateExperience: (openingId: string, itemId: string, data: Partial<Omit<ORExperience, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeExperienceResponse>(`${base(openingId)}/experience/${itemId}`, {
      method: 'PATCH',
      body: {
        company: data.company ?? undefined,
        title: data.title ?? undefined,
        location: data.location ?? undefined,
        start_date: data.start_date ?? undefined,
        end_date: data.end_date ?? undefined,
        is_current: data.is_current ?? undefined,
        description: data.description ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapExperience),
  deleteExperience: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/experience/${itemId}`, { method: 'DELETE' }),

  // Projects
  getProjects: (openingId: string) => apiRequest<OpeningResumeProjectResponse[]>(`${base(openingId)}/projects`).then(rows => rows.map(mapProject)),
  createProject: (openingId: string, data: Omit<ORProject, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeProjectResponse>(`${base(openingId)}/projects`, {
      method: 'POST',
      body: {
        name: data.title,
        description: data.description ?? null,
        url: data.url ?? null,
        start_date: data.start_date ?? null,
        end_date: data.end_date ?? null,
        technologies: data.technologies ?? [],
        display_order: data.display_order ?? 0,
      },
    }).then(mapProject),
  updateProject: (openingId: string, itemId: string, data: Partial<Omit<ORProject, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeProjectResponse>(`${base(openingId)}/projects/${itemId}`, {
      method: 'PATCH',
      body: {
        name: data.title ?? undefined,
        description: data.description ?? undefined,
        url: data.url ?? undefined,
        start_date: data.start_date ?? undefined,
        end_date: data.end_date ?? undefined,
        technologies: data.technologies ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapProject),
  deleteProject: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/projects/${itemId}`, { method: 'DELETE' }),

  // Research
  getResearch: (openingId: string) => apiRequest<OpeningResumeResearchResponse[]>(`${base(openingId)}/research`).then(rows => rows.map(mapResearch)),
  createResearch: (openingId: string, data: Omit<ORResearch, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeResearchResponse>(`${base(openingId)}/research`, {
      method: 'POST',
      body: {
        title: data.title,
        publication: data.publication ?? null,
        published_date: data.published_date ?? null,
        url: data.url ?? null,
        description: data.description ?? null,
        display_order: data.display_order ?? 0,
      },
    }).then(mapResearch),
  updateResearch: (openingId: string, itemId: string, data: Partial<Omit<ORResearch, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeResearchResponse>(`${base(openingId)}/research/${itemId}`, {
      method: 'PATCH',
      body: {
        title: data.title ?? undefined,
        publication: data.publication ?? undefined,
        published_date: data.published_date ?? undefined,
        url: data.url ?? undefined,
        description: data.description ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapResearch),
  deleteResearch: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/research/${itemId}`, { method: 'DELETE' }),

  // Certifications
  getCertifications: (openingId: string) => apiRequest<OpeningResumeCertificationResponse[]>(`${base(openingId)}/certifications`).then(rows => rows.map(mapCertification)),
  createCertification: (openingId: string, data: Omit<ORCertification, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeCertificationResponse>(`${base(openingId)}/certifications`, {
      method: 'POST',
      body: {
        name: data.name,
        issuer: data.issuing_organization ?? null,
        issue_date: data.issue_date ?? null,
        expiry_date: data.expiry_date ?? null,
        credential_id: data.credential_id ?? null,
        url: data.credential_url ?? null,
        display_order: data.display_order ?? 0,
      },
    }).then(mapCertification),
  updateCertification: (openingId: string, itemId: string, data: Partial<Omit<ORCertification, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeCertificationResponse>(`${base(openingId)}/certifications/${itemId}`, {
      method: 'PATCH',
      body: {
        name: data.name ?? undefined,
        issuer: data.issuing_organization ?? undefined,
        issue_date: data.issue_date ?? undefined,
        expiry_date: data.expiry_date ?? undefined,
        credential_id: data.credential_id ?? undefined,
        url: data.credential_url ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapCertification),
  deleteCertification: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/certifications/${itemId}`, { method: 'DELETE' }),

  // Skills (CRUD list/create/update/delete)
  getSkills: (openingId: string) => apiRequest<OpeningResumeSkillResponse[]>(`${base(openingId)}/skills`).then(rows => rows.map(mapSkill)),
  createSkill: (openingId: string, data: Omit<ORSkillItem, 'id' | 'resume_id'>) =>
    apiRequest<OpeningResumeSkillResponse>(`${base(openingId)}/skills`, {
      method: 'POST',
      body: {
        category: data.category,
        name: data.name,
        proficiency_level: data.proficiency_level ?? null,
        display_order: data.display_order ?? 0,
      },
    }).then(mapSkill),
  updateSkill: (openingId: string, entryId: string, data: Partial<Omit<ORSkillItem, 'id' | 'resume_id'>>) =>
    apiRequest<OpeningResumeSkillResponse>(`${base(openingId)}/skills/${entryId}`, {
      method: 'PATCH',
      body: {
        category: data.category ?? undefined,
        name: data.name ?? undefined,
        proficiency_level: data.proficiency_level ?? undefined,
        display_order: data.display_order ?? undefined,
      },
    }).then(mapSkill),
  deleteSkill: (openingId: string, entryId: string) =>
    apiRequest<void>(`${base(openingId)}/skills/${entryId}`, { method: 'DELETE' }),
}
