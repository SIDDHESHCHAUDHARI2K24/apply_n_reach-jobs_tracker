import { apiRequest, apiRequestBlob } from '@core/http/client'
import { profileApi } from '@features/user-profile/profileApi'
import type {
  JobProfile,
  CreateJobProfileRequest,
  ResumeMetadata,
  ImportResult,
  JPPersonal,
  JPEducation,
  JPExperience,
  JPProject,
  JPResearch,
  JPCertification,
  JPSkills,
} from './types'
import type {
  JobProfileCertificationResponse,
  JobProfileCreate,
  JobProfileEducationResponse,
  JobProfileExperienceResponse,
  JobProfilePersonalResponse,
  JobProfileProjectResponse,
  JobProfileResearchResponse,
  JobProfileResponse,
  JobProfileSkillItemResponse,
  JobProfileSkillsUpdate,
  PaginatedJobProfileResponse,
} from '@generated/contracts'

const toStringId = (id: number) => String(id)

function mapJobProfile(row: JobProfileResponse): JobProfile {
  return {
    id: toStringId(row.id),
    user_id: toStringId(row.user_id),
    title: row.profile_name,
    status: row.status as JobProfile['status'],
    created_at: row.created_at,
    updated_at: row.updated_at,
  }
}

function mapPersonal(row: JobProfilePersonalResponse): JPPersonal {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    full_name: row.full_name ?? null,
    email: row.email ?? null,
    phone: (row as any).phone ?? null,
    location: (row as any).location ?? null,
    linkedin_url: row.linkedin_url ?? null,
    github_url: row.github_url ?? null,
    portfolio_url: row.portfolio_url ?? null,
    summary: (row as any).summary ?? null,
    updated_at: row.updated_at,
  }
}

function mapEducation(row: JobProfileEducationResponse): JPEducation {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    institution: row.university_name,
    degree: row.degree_type,
    field_of_study: row.major,
    start_date: row.start_month_year,
    end_date: row.end_month_year ?? null,
    gpa: null,
    bullet_points: row.bullet_points ?? [],
  }
}

function mapExperience(row: JobProfileExperienceResponse): JPExperience {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    company: row.company_name,
    title: row.role_title,
    location: row.location ?? null,
    start_date: row.start_month_year,
    end_date: row.end_month_year ?? null,
    is_current: !row.end_month_year,
    bullet_points: row.bullet_points ?? [],
  }
}

function mapProject(row: JobProfileProjectResponse): JPProject {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    title: row.project_name,
    description: row.description ?? null,
    technologies: (row as any).technologies ?? [],
    url: row.reference_links?.[0] ?? null,
    start_date: row.start_month_year ?? null,
    end_date: row.end_month_year ?? null,
    bullet_points: (row as any).bullet_points ?? [],
  }
}

function mapResearch(row: JobProfileResearchResponse): JPResearch {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    title: row.paper_name,
    institution: (row as any).institution ?? null,
    journal: (row as any).journal ?? null,
    year: (row as any).year ?? null,
    description: row.description ?? null,
    url: row.publication_link ?? null,
    bullet_points: [],
    reference_links: [],
  }
}

function mapCertification(row: JobProfileCertificationResponse): JPCertification {
  return {
    id: toStringId(row.id),
    job_profile_id: toStringId(row.job_profile_id),
    name: row.certification_name,
    issuing_organization: null,
    issue_date: null,
    expiry_date: null,
    credential_id: null,
    credential_url: row.verification_link,
  }
}

function mapImportResult(result: { imported: number[]; skipped: number[]; not_found: number[] }): ImportResult {
  return {
    imported_count: result.imported.length,
    skipped_count: result.skipped.length + result.not_found.length,
  }
}

function mapResumeMetadata(row: {
  job_profile_id: number
  status?: 'completed'
  template_name: string
  rendered_at: string
  layout_json: Record<string, unknown>
  error_message?: string | null
  created_at?: string | null
  updated_at?: string | null
}): ResumeMetadata {
  return {
    job_profile_id: toStringId(row.job_profile_id),
    status: row.status ?? 'completed',
    template_name: row.template_name,
    rendered_at: row.rendered_at,
    layout_json: row.layout_json ?? {},
    error_message: row.error_message ?? null,
    created_at: row.created_at ?? null,
    updated_at: row.updated_at ?? null,
  }
}

export const jobProfileApi = {
  // List + CRUD
  list: async (params?: { limit?: number; offset?: number; status?: string }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.offset != null) qs.set('offset', String(params.offset))
    if (params?.status) qs.set('status', params.status)
    const query = qs.toString()
    const response = await apiRequest<PaginatedJobProfileResponse>(`/job-profiles${query ? `?${query}` : ''}`)
    return { ...response, items: response.items.map(mapJobProfile) }
  },
  create: async (data: CreateJobProfileRequest) => {
    const payload: JobProfileCreate = {
      profile_name: data.title,
      target_role: null,
      target_company: null,
      job_posting_url: null,
    }
    const response = await apiRequest<JobProfileResponse>('/job-profiles', { method: 'POST', body: payload })
    return mapJobProfile(response)
  },
  activate: async (id: string) =>
    mapJobProfile(await apiRequest<JobProfileResponse>(`/job-profiles/${id}/status/activate`, { method: 'POST' })),
  archive: async (id: string) =>
    mapJobProfile(await apiRequest<JobProfileResponse>(`/job-profiles/${id}/status/archive`, { method: 'POST' })),
  remove: (id: string) =>
    apiRequest<void>(`/job-profiles/${id}`, { method: 'DELETE' }),

  // Personal
  getPersonal: async (jpId: string) => mapPersonal(await apiRequest<JobProfilePersonalResponse>(`/job-profiles/${jpId}/personal`)),
  updatePersonal: async (jpId: string, data: Partial<JPPersonal>) => {
    const response = await apiRequest<JobProfilePersonalResponse>(`/job-profiles/${jpId}/personal`, {
      method: 'PATCH',
      body: {
        full_name: data.full_name ?? undefined,
        email: data.email ?? undefined,
        linkedin_url: data.linkedin_url ?? undefined,
        github_url: data.github_url ?? undefined,
        portfolio_url: data.portfolio_url ?? undefined,
        summary: data.summary ?? undefined,
        location: data.location ?? undefined,
        phone: data.phone ?? undefined,
      },
    })
    return mapPersonal(response)
  },

  // Education
  getEducation: async (jpId: string) => (await apiRequest<JobProfileEducationResponse[]>(`/job-profiles/${jpId}/education`)).map(mapEducation),
  createEducation: async (jpId: string, data: Omit<JPEducation, 'id' | 'job_profile_id'>) => {
    const response = await apiRequest<JobProfileEducationResponse>(`/job-profiles/${jpId}/education`, {
      method: 'POST',
      body: {
        university_name: data.institution,
        major: data.field_of_study ?? '',
        degree_type: data.degree,
        start_month_year: data.start_date ?? '',
        end_month_year: data.end_date ?? null,
        bullet_points: data.bullet_points ?? [],
        reference_links: [],
      },
    })
    return mapEducation(response)
  },
  updateEducation: async (jpId: string, itemId: string, data: Partial<Omit<JPEducation, 'id' | 'job_profile_id'>>) => {
    const response = await apiRequest<JobProfileEducationResponse>(`/job-profiles/${jpId}/education/${itemId}`, {
      method: 'PATCH',
      body: {
        university_name: data.institution ?? undefined,
        major: data.field_of_study ?? undefined,
        degree_type: data.degree ?? undefined,
        start_month_year: data.start_date ?? undefined,
        end_month_year: data.end_date ?? undefined,
        bullet_points: data.bullet_points ?? undefined,
      },
    })
    return mapEducation(response)
  },
  deleteEducation: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/education/${itemId}`, { method: 'DELETE' }),
  importEducation: async (jpId: string) => {
    const sourceIds = (await profileApi.getEducation()).map(item => Number(item.id)).filter(Number.isFinite)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/education/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Experience
  getExperience: async (jpId: string) => (await apiRequest<JobProfileExperienceResponse[]>(`/job-profiles/${jpId}/experience`)).map(mapExperience),
  createExperience: async (jpId: string, data: Omit<JPExperience, 'id' | 'job_profile_id'>) => {
    const response = await apiRequest<JobProfileExperienceResponse>(`/job-profiles/${jpId}/experience`, {
      method: 'POST',
      body: {
        role_title: data.title,
        company_name: data.company,
        location: data.location ?? null,
        start_month_year: data.start_date ?? '',
        end_month_year: data.end_date ?? null,
        context: '',
        work_sample_links: [],
        bullet_points: data.bullet_points ?? [],
      },
    })
    return mapExperience(response)
  },
  updateExperience: async (jpId: string, itemId: string, data: Partial<Omit<JPExperience, 'id' | 'job_profile_id'>>) => {
    const response = await apiRequest<JobProfileExperienceResponse>(`/job-profiles/${jpId}/experience/${itemId}`, {
      method: 'PATCH',
      body: {
        role_title: data.title ?? undefined,
        company_name: data.company ?? undefined,
        location: data.location ?? undefined,
        start_month_year: data.start_date ?? undefined,
        end_month_year: data.end_date ?? undefined,
        bullet_points: data.bullet_points ?? undefined,
      },
    })
    return mapExperience(response)
  },
  deleteExperience: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/experience/${itemId}`, { method: 'DELETE' }),
  importExperience: async (jpId: string) => {
    const sourceIds = (await profileApi.getExperience()).map(item => Number(item.id)).filter(Number.isFinite)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/experience/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Projects
  getProjects: async (jpId: string) => (await apiRequest<JobProfileProjectResponse[]>(`/job-profiles/${jpId}/projects`)).map(mapProject),
  createProject: async (jpId: string, data: Omit<JPProject, 'id' | 'job_profile_id'>) => {
    const response = await apiRequest<JobProfileProjectResponse>(`/job-profiles/${jpId}/projects`, {
      method: 'POST',
      body: {
        project_name: data.title,
        description: data.description ?? '',
        start_month_year: data.start_date ?? null,
        end_month_year: data.end_date ?? null,
        reference_links: data.url ? [data.url] : [],
        technologies: data.technologies ?? [],
      },
    })
    return mapProject(response)
  },
  updateProject: async (jpId: string, itemId: string, data: Partial<Omit<JPProject, 'id' | 'job_profile_id'>>) => {
    const response = await apiRequest<JobProfileProjectResponse>(`/job-profiles/${jpId}/projects/${itemId}`, {
      method: 'PATCH',
      body: {
        project_name: data.title ?? undefined,
        description: data.description ?? undefined,
        start_month_year: data.start_date ?? undefined,
        end_month_year: data.end_date ?? undefined,
        reference_links: data.url ? [data.url] : undefined,
        technologies: data.technologies ?? undefined,
      },
    })
    return mapProject(response)
  },
  deleteProject: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/projects/${itemId}`, { method: 'DELETE' }),
  importProjects: async (jpId: string) => {
    const sourceIds = (await profileApi.getProjects()).map(item => Number(item.id)).filter(Number.isFinite)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/projects/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Research
  getResearch: async (jpId: string) => (await apiRequest<JobProfileResearchResponse[]>(`/job-profiles/${jpId}/research`)).map(mapResearch),
  createResearch: async (jpId: string, data: Omit<JPResearch, 'id' | 'job_profile_id'>) => {
    const response = await apiRequest<JobProfileResearchResponse>(`/job-profiles/${jpId}/research`, {
      method: 'POST',
      body: {
        paper_name: data.title,
        publication_link: data.url ?? '',
        description: data.description ?? null,
        journal: (data as any).journal ?? undefined,
        year: (data as any).year ?? undefined,
      },
    })
    return mapResearch(response)
  },
  updateResearch: async (jpId: string, itemId: string, data: Partial<Omit<JPResearch, 'id' | 'job_profile_id'>>) => {
    const response = await apiRequest<JobProfileResearchResponse>(`/job-profiles/${jpId}/research/${itemId}`, {
      method: 'PATCH',
      body: {
        paper_name: data.title ?? undefined,
        publication_link: data.url ?? undefined,
        description: data.description ?? undefined,
        journal: (data as any).journal ?? undefined,
        year: (data as any).year ?? undefined,
      },
    })
    return mapResearch(response)
  },
  deleteResearch: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/research/${itemId}`, { method: 'DELETE' }),
  importResearch: async (jpId: string) => {
    const sourceIds = (await profileApi.getResearch()).map(item => Number(item.id)).filter(Number.isFinite)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/research/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Certifications
  getCertifications: async (jpId: string) => (await apiRequest<JobProfileCertificationResponse[]>(`/job-profiles/${jpId}/certifications`)).map(mapCertification),
  createCertification: async (jpId: string, data: Omit<JPCertification, 'id' | 'job_profile_id'>) => {
    const response = await apiRequest<JobProfileCertificationResponse>(`/job-profiles/${jpId}/certifications`, {
      method: 'POST',
      body: {
        certification_name: data.name,
        verification_link: data.credential_url ?? '',
      },
    })
    return mapCertification(response)
  },
  updateCertification: async (jpId: string, itemId: string, data: Partial<Omit<JPCertification, 'id' | 'job_profile_id'>>) => {
    const response = await apiRequest<JobProfileCertificationResponse>(`/job-profiles/${jpId}/certifications/${itemId}`, {
      method: 'PATCH',
      body: {
        certification_name: data.name ?? undefined,
        verification_link: data.credential_url ?? undefined,
      },
    })
    return mapCertification(response)
  },
  deleteCertification: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/certifications/${itemId}`, { method: 'DELETE' }),
  importCertifications: async (jpId: string) => {
    const sourceIds = (await profileApi.getCertifications()).map(item => Number(item.id)).filter(Number.isFinite)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/certifications/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Skills
  getSkills: async (jpId: string) => {
    const rows = await apiRequest<JobProfileSkillItemResponse[]>(`/job-profiles/${jpId}/skills`)
    return { skills: rows.map(row => row.name) }
  },
  updateSkills: async (jpId: string, skills: string[]) => {
    const payload: JobProfileSkillsUpdate = {
      skills: skills.map((name, index) => ({ kind: 'technical', name, sort_order: index })),
    }
    const rows = await apiRequest<JobProfileSkillItemResponse[]>(`/job-profiles/${jpId}/skills`, { method: 'PATCH', body: payload })
    return { skills: rows.map(row => row.name) } as JPSkills
  },
  importSkills: async (jpId: string) => {
    const sourceRows = await apiRequest<{ id: number }[]>('/profile/skills')
    const sourceIds = sourceRows.map(row => row.id)
    const result = await apiRequest<{ imported: number[]; skipped: number[]; not_found: number[] }>(`/job-profiles/${jpId}/skills/import`, {
      method: 'POST',
      body: { source_ids: sourceIds },
    })
    return mapImportResult(result)
  },

  // Resume render
  triggerRender: async (jpId: string) =>
    mapResumeMetadata(await apiRequest<{
      job_profile_id: number
      status?: 'completed'
      template_name: string
      rendered_at: string
      layout_json: Record<string, unknown>
      error_message?: string | null
      created_at?: string | null
      updated_at?: string | null
    }>(`/job-profiles/${jpId}/latex-resume/render`, { method: 'POST' })),
  getResumeMetadata: async (jpId: string) =>
    mapResumeMetadata(await apiRequest<{
      job_profile_id: number
      status?: 'completed'
      template_name: string
      rendered_at: string
      layout_json: Record<string, unknown>
      error_message?: string | null
      created_at?: string | null
      updated_at?: string | null
    }>(`/job-profiles/${jpId}/latex-resume`)),
  downloadPdf: (jpId: string) =>
    apiRequestBlob(`/job-profiles/${jpId}/latex-resume/pdf`),
}
