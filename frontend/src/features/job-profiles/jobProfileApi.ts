import { apiRequest, apiRequestBlob } from '@core/http/client'
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

export const jobProfileApi = {
  // List + CRUD
  list: (params?: { limit?: number; offset?: number; status?: string }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.offset != null) qs.set('offset', String(params.offset))
    if (params?.status) qs.set('status', params.status)
    const query = qs.toString()
    return apiRequest<JobProfile[]>(`/job-profiles${query ? `?${query}` : ''}`)
  },
  create: (data: CreateJobProfileRequest) =>
    apiRequest<JobProfile>('/job-profiles', { method: 'POST', body: data }),
  remove: (id: string) =>
    apiRequest<void>(`/job-profiles/${id}`, { method: 'DELETE' }),

  // Personal
  getPersonal: (jpId: string) => apiRequest<JPPersonal>(`/job-profiles/${jpId}/personal`),
  updatePersonal: (jpId: string, data: Partial<JPPersonal>) =>
    apiRequest<JPPersonal>(`/job-profiles/${jpId}/personal`, { method: 'PATCH', body: data }),

  // Education
  getEducation: (jpId: string) => apiRequest<JPEducation[]>(`/job-profiles/${jpId}/education`),
  createEducation: (jpId: string, data: Omit<JPEducation, 'id' | 'job_profile_id'>) =>
    apiRequest<JPEducation>(`/job-profiles/${jpId}/education`, { method: 'POST', body: data }),
  updateEducation: (jpId: string, itemId: string, data: Partial<Omit<JPEducation, 'id' | 'job_profile_id'>>) =>
    apiRequest<JPEducation>(`/job-profiles/${jpId}/education/${itemId}`, { method: 'PATCH', body: data }),
  deleteEducation: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/education/${itemId}`, { method: 'DELETE' }),
  importEducation: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/education/import`, { method: 'POST' }),

  // Experience
  getExperience: (jpId: string) => apiRequest<JPExperience[]>(`/job-profiles/${jpId}/experience`),
  createExperience: (jpId: string, data: Omit<JPExperience, 'id' | 'job_profile_id'>) =>
    apiRequest<JPExperience>(`/job-profiles/${jpId}/experience`, { method: 'POST', body: data }),
  updateExperience: (jpId: string, itemId: string, data: Partial<Omit<JPExperience, 'id' | 'job_profile_id'>>) =>
    apiRequest<JPExperience>(`/job-profiles/${jpId}/experience/${itemId}`, { method: 'PATCH', body: data }),
  deleteExperience: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/experience/${itemId}`, { method: 'DELETE' }),
  importExperience: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/experience/import`, { method: 'POST' }),

  // Projects
  getProjects: (jpId: string) => apiRequest<JPProject[]>(`/job-profiles/${jpId}/projects`),
  createProject: (jpId: string, data: Omit<JPProject, 'id' | 'job_profile_id'>) =>
    apiRequest<JPProject>(`/job-profiles/${jpId}/projects`, { method: 'POST', body: data }),
  updateProject: (jpId: string, itemId: string, data: Partial<Omit<JPProject, 'id' | 'job_profile_id'>>) =>
    apiRequest<JPProject>(`/job-profiles/${jpId}/projects/${itemId}`, { method: 'PATCH', body: data }),
  deleteProject: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/projects/${itemId}`, { method: 'DELETE' }),
  importProjects: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/projects/import`, { method: 'POST' }),

  // Research
  getResearch: (jpId: string) => apiRequest<JPResearch[]>(`/job-profiles/${jpId}/research`),
  createResearch: (jpId: string, data: Omit<JPResearch, 'id' | 'job_profile_id'>) =>
    apiRequest<JPResearch>(`/job-profiles/${jpId}/research`, { method: 'POST', body: data }),
  updateResearch: (jpId: string, itemId: string, data: Partial<Omit<JPResearch, 'id' | 'job_profile_id'>>) =>
    apiRequest<JPResearch>(`/job-profiles/${jpId}/research/${itemId}`, { method: 'PATCH', body: data }),
  deleteResearch: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/research/${itemId}`, { method: 'DELETE' }),
  importResearch: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/research/import`, { method: 'POST' }),

  // Certifications
  getCertifications: (jpId: string) => apiRequest<JPCertification[]>(`/job-profiles/${jpId}/certifications`),
  createCertification: (jpId: string, data: Omit<JPCertification, 'id' | 'job_profile_id'>) =>
    apiRequest<JPCertification>(`/job-profiles/${jpId}/certifications`, { method: 'POST', body: data }),
  updateCertification: (jpId: string, itemId: string, data: Partial<Omit<JPCertification, 'id' | 'job_profile_id'>>) =>
    apiRequest<JPCertification>(`/job-profiles/${jpId}/certifications/${itemId}`, { method: 'PATCH', body: data }),
  deleteCertification: (jpId: string, itemId: string) =>
    apiRequest<void>(`/job-profiles/${jpId}/certifications/${itemId}`, { method: 'DELETE' }),
  importCertifications: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/certifications/import`, { method: 'POST' }),

  // Skills
  getSkills: (jpId: string) => apiRequest<JPSkills>(`/job-profiles/${jpId}/skills`),
  updateSkills: (jpId: string, skills: string[]) =>
    apiRequest<JPSkills>(`/job-profiles/${jpId}/skills`, { method: 'PATCH', body: { skills } }),
  importSkills: (jpId: string) =>
    apiRequest<ImportResult>(`/job-profiles/${jpId}/skills/import`, { method: 'POST' }),

  // Resume render
  triggerRender: (jpId: string) =>
    apiRequest<ResumeMetadata>(`/job-profiles/${jpId}/resume/render`, { method: 'POST' }),
  getResumeMetadata: (jpId: string) =>
    apiRequest<ResumeMetadata>(`/job-profiles/${jpId}/resume/metadata`),
  downloadPdf: (jpId: string) =>
    apiRequestBlob(`/job-profiles/${jpId}/resume/pdf`),
}
