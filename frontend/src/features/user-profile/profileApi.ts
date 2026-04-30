import { apiRequest } from '@core/http/client'
import type {
  ProfileSummary,
  PersonalDetails,
  Education,
  Experience,
  Project,
  Research,
  Certification,
} from './types'
import type {
  UserProfileCertificationCreate,
  UserProfileCertificationResponse,
  UserProfileCertificationUpdate,
  UserProfileEducationCreate,
  UserProfileEducationResponse,
  UserProfileEducationUpdate,
  UserProfileExperienceCreate,
  UserProfileExperienceResponse,
  UserProfileExperienceUpdate,
  UserProfilePersonalResponse,
  UserProfilePersonalUpdate,
  UserProfileProjectCreate,
  UserProfileProjectResponse,
  UserProfileProjectUpdate,
  UserProfileResearchCreate,
  UserProfileResearchResponse,
  UserProfileResearchUpdate,
  UserProfileSkillItemResponse,
  UserProfileSkillsUpdate,
} from '@generated/contracts'

const toStringId = (id: number) => String(id)

function mapPersonal(response: UserProfilePersonalResponse): PersonalDetails {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    full_name: response.full_name ?? null,
    email: response.email ?? null,
    phone: null,
    location: null,
    linkedin_url: response.linkedin_url ?? null,
    github_url: response.github_url ?? null,
    portfolio_url: response.portfolio_url ?? null,
    summary: null,
    created_at: '',
    updated_at: '',
  }
}

function mapEducation(response: UserProfileEducationResponse): Education {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    institution: response.university_name,
    degree: response.degree_type,
    field_of_study: response.major,
    start_date: response.start_month_year,
    end_date: response.end_month_year ?? null,
    gpa: null,
    bullet_points: response.bullet_points ?? [],
    created_at: response.created_at,
    updated_at: response.updated_at,
  }
}

function mapExperience(response: UserProfileExperienceResponse): Experience {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    company: response.company_name,
    title: response.role_title,
    location: response.location ?? null,
    start_date: response.start_month_year,
    end_date: response.end_month_year ?? null,
    is_current: !response.end_month_year,
    bullet_points: response.bullet_points ?? [],
    created_at: response.created_at,
    updated_at: response.updated_at,
  }
}

function mapProject(response: UserProfileProjectResponse): Project {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    title: response.project_name,
    description: response.description ?? null,
    technologies: [],
    url: response.reference_links?.[0] ?? null,
    start_date: response.start_month_year,
    end_date: response.end_month_year ?? null,
    bullet_points: [],
    created_at: response.created_at,
    updated_at: response.updated_at,
  }
}

function mapResearch(response: UserProfileResearchResponse): Research {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    title: response.paper_name,
    institution: null,
    journal: null,
    year: null,
    description: response.description ?? null,
    url: response.publication_link,
    bullet_points: [],
    reference_links: [],
    created_at: response.created_at,
    updated_at: response.updated_at,
  }
}

function mapCertification(response: UserProfileCertificationResponse): Certification {
  return {
    id: toStringId(response.id),
    profile_id: toStringId(response.profile_id),
    name: response.certification_name,
    issuing_organization: null,
    issue_date: null,
    expiry_date: null,
    credential_id: null,
    credential_url: response.verification_link,
    created_at: response.created_at,
    updated_at: response.updated_at,
  }
}

export interface SkillsData {
  skills: string[]
}

export const profileApi = {
  // Bootstrap
  bootstrapProfile: () =>
    apiRequest<ProfileSummary>('/profile', { method: 'POST' }),

  getProfileSummary: () =>
    apiRequest<ProfileSummary>('/profile/summary'),

  // Personal
  getPersonal: async () => {
    const data = await apiRequest<UserProfilePersonalResponse>('/profile/personal')
    return mapPersonal(data)
  },

  updatePersonal: async (data: Partial<Omit<PersonalDetails, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfilePersonalUpdate = {
      full_name: data.full_name ?? undefined,
      email: data.email ?? undefined,
      linkedin_url: data.linkedin_url ?? undefined,
      github_url: data.github_url ?? undefined,
      portfolio_url: data.portfolio_url ?? undefined,
    }
    const response = await apiRequest<UserProfilePersonalResponse>('/profile/personal', { method: 'PATCH', body: payload })
    return mapPersonal(response)
  },

  // Education
  getEducation: async () => {
    const rows = await apiRequest<UserProfileEducationResponse[]>('/profile/education')
    return rows.map(mapEducation)
  },

  createEducation: async (data: Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    const payload: UserProfileEducationCreate = {
      university_name: data.institution,
      major: data.field_of_study ?? '',
      degree_type: data.degree,
      start_month_year: data.start_date ?? '',
      end_month_year: data.end_date ?? null,
      bullet_points: data.bullet_points ?? [],
      reference_links: [],
    }
    const response = await apiRequest<UserProfileEducationResponse>('/profile/education', { method: 'POST', body: payload })
    return mapEducation(response)
  },

  updateEducation: async (id: string, data: Partial<Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfileEducationUpdate = {
      university_name: data.institution ?? undefined,
      major: data.field_of_study ?? undefined,
      degree_type: data.degree ?? undefined,
      start_month_year: data.start_date ?? undefined,
      end_month_year: data.end_date ?? undefined,
      bullet_points: data.bullet_points ?? undefined,
    }
    const response = await apiRequest<UserProfileEducationResponse>(`/profile/education/${id}`, { method: 'PATCH', body: payload })
    return mapEducation(response)
  },

  deleteEducation: (id: string) =>
    apiRequest<void>(`/profile/education/${id}`, { method: 'DELETE' }),

  // Experience
  getExperience: async () => {
    const rows = await apiRequest<UserProfileExperienceResponse[]>('/profile/experience')
    return rows.map(mapExperience)
  },

  createExperience: async (data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    const payload: UserProfileExperienceCreate = {
      role_title: data.title,
      company_name: data.company,
      location: data.location ?? null,
      start_month_year: data.start_date ?? '',
      end_month_year: data.end_date ?? null,
      context: '',
      work_sample_links: [],
      bullet_points: data.bullet_points ?? [],
    }
    const response = await apiRequest<UserProfileExperienceResponse>('/profile/experience', { method: 'POST', body: payload })
    return mapExperience(response)
  },

  updateExperience: async (id: string, data: Partial<Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfileExperienceUpdate = {
      role_title: data.title ?? undefined,
      company_name: data.company ?? undefined,
      location: data.location ?? undefined,
      start_month_year: data.start_date ?? undefined,
      end_month_year: data.end_date ?? undefined,
      bullet_points: data.bullet_points ?? undefined,
    }
    const response = await apiRequest<UserProfileExperienceResponse>(`/profile/experience/${id}`, { method: 'PATCH', body: payload })
    return mapExperience(response)
  },

  deleteExperience: (id: string) =>
    apiRequest<void>(`/profile/experience/${id}`, { method: 'DELETE' }),

  // Projects
  getProjects: async () => {
    const rows = await apiRequest<UserProfileProjectResponse[]>('/profile/projects')
    return rows.map(mapProject)
  },

  createProject: async (data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    const payload: UserProfileProjectCreate = {
      project_name: data.title,
      description: data.description ?? '',
      start_month_year: data.start_date ?? '',
      end_month_year: data.end_date ?? null,
      reference_links: data.url ? [data.url] : [],
    }
    const response = await apiRequest<UserProfileProjectResponse>('/profile/projects', { method: 'POST', body: payload })
    return mapProject(response)
  },

  updateProject: async (id: string, data: Partial<Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfileProjectUpdate = {
      project_name: data.title ?? undefined,
      description: data.description ?? undefined,
      start_month_year: data.start_date ?? undefined,
      end_month_year: data.end_date ?? undefined,
      reference_links: data.url ? [data.url] : undefined,
    }
    const response = await apiRequest<UserProfileProjectResponse>(`/profile/projects/${id}`, { method: 'PATCH', body: payload })
    return mapProject(response)
  },

  deleteProject: (id: string) =>
    apiRequest<void>(`/profile/projects/${id}`, { method: 'DELETE' }),

  // Research
  getResearch: async () => {
    const rows = await apiRequest<UserProfileResearchResponse[]>('/profile/research')
    return rows.map(mapResearch)
  },

  createResearch: async (data: Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    const payload: UserProfileResearchCreate = {
      paper_name: data.title,
      publication_link: data.url ?? '',
      description: data.description ?? null,
    }
    const response = await apiRequest<UserProfileResearchResponse>('/profile/research', { method: 'POST', body: payload })
    return mapResearch(response)
  },

  updateResearch: async (id: string, data: Partial<Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfileResearchUpdate = {
      paper_name: data.title ?? undefined,
      publication_link: data.url ?? undefined,
      description: data.description ?? undefined,
    }
    const response = await apiRequest<UserProfileResearchResponse>(`/profile/research/${id}`, { method: 'PATCH', body: payload })
    return mapResearch(response)
  },

  deleteResearch: (id: string) =>
    apiRequest<void>(`/profile/research/${id}`, { method: 'DELETE' }),

  // Certifications
  getCertifications: async () => {
    const rows = await apiRequest<UserProfileCertificationResponse[]>('/profile/certifications')
    return rows.map(mapCertification)
  },

  createCertification: async (data: Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    const payload: UserProfileCertificationCreate = {
      certification_name: data.name,
      verification_link: data.credential_url ?? '',
    }
    const response = await apiRequest<UserProfileCertificationResponse>('/profile/certifications', { method: 'POST', body: payload })
    return mapCertification(response)
  },

  updateCertification: async (id: string, data: Partial<Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    const payload: UserProfileCertificationUpdate = {
      certification_name: data.name ?? undefined,
      verification_link: data.credential_url ?? undefined,
    }
    const response = await apiRequest<UserProfileCertificationResponse>(`/profile/certifications/${id}`, { method: 'PATCH', body: payload })
    return mapCertification(response)
  },

  deleteCertification: (id: string) =>
    apiRequest<void>(`/profile/certifications/${id}`, { method: 'DELETE' }),

  // Skills
  getSkills: async () => {
    const rows = await apiRequest<UserProfileSkillItemResponse[]>('/profile/skills')
    return { skills: rows.map(row => row.name) }
  },

  updateSkills: async (skills: string[]) => {
    const payload: UserProfileSkillsUpdate = {
      skills: skills.map((name, index) => ({
        kind: 'technical',
        name,
        sort_order: index,
      })),
    }
    const rows = await apiRequest<UserProfileSkillItemResponse[]>('/profile/skills', { method: 'PATCH', body: payload })
    return { skills: rows.map(row => row.name) }
  },
}
