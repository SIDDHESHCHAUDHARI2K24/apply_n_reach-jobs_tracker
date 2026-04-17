import { apiRequest } from '@core/http/client'
import type { OpeningResume, ORPersonal, OREducation, ORExperience, ORProject, ORResearch, ORCertification, ORSkills } from './types'

const base = (openingId: string) => `/job-openings/${openingId}/resume`

export const openingResumeApi = {
  create: (openingId: string, sourceJobProfileId?: string) => {
    const qs = sourceJobProfileId ? `?source_job_profile_id=${sourceJobProfileId}` : ''
    return apiRequest<OpeningResume>(`${base(openingId)}${qs}`, { method: 'POST' })
  },
  get: (openingId: string) =>
    apiRequest<OpeningResume>(`${base(openingId)}`),

  // Personal (PUT)
  getPersonal: (openingId: string) => apiRequest<ORPersonal>(`${base(openingId)}/personal`),
  updatePersonal: (openingId: string, data: Partial<ORPersonal>) =>
    apiRequest<ORPersonal>(`${base(openingId)}/personal`, { method: 'PUT', body: data }),

  // Education
  getEducation: (openingId: string) => apiRequest<OREducation[]>(`${base(openingId)}/education`),
  createEducation: (openingId: string, data: Omit<OREducation, 'id' | 'resume_id'>) =>
    apiRequest<OREducation>(`${base(openingId)}/education`, { method: 'POST', body: data }),
  updateEducation: (openingId: string, itemId: string, data: Partial<Omit<OREducation, 'id' | 'resume_id'>>) =>
    apiRequest<OREducation>(`${base(openingId)}/education/${itemId}`, { method: 'PATCH', body: data }),
  deleteEducation: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/education/${itemId}`, { method: 'DELETE' }),

  // Experience
  getExperience: (openingId: string) => apiRequest<ORExperience[]>(`${base(openingId)}/experience`),
  createExperience: (openingId: string, data: Omit<ORExperience, 'id' | 'resume_id'>) =>
    apiRequest<ORExperience>(`${base(openingId)}/experience`, { method: 'POST', body: data }),
  updateExperience: (openingId: string, itemId: string, data: Partial<Omit<ORExperience, 'id' | 'resume_id'>>) =>
    apiRequest<ORExperience>(`${base(openingId)}/experience/${itemId}`, { method: 'PATCH', body: data }),
  deleteExperience: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/experience/${itemId}`, { method: 'DELETE' }),

  // Projects
  getProjects: (openingId: string) => apiRequest<ORProject[]>(`${base(openingId)}/projects`),
  createProject: (openingId: string, data: Omit<ORProject, 'id' | 'resume_id'>) =>
    apiRequest<ORProject>(`${base(openingId)}/projects`, { method: 'POST', body: data }),
  updateProject: (openingId: string, itemId: string, data: Partial<Omit<ORProject, 'id' | 'resume_id'>>) =>
    apiRequest<ORProject>(`${base(openingId)}/projects/${itemId}`, { method: 'PATCH', body: data }),
  deleteProject: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/projects/${itemId}`, { method: 'DELETE' }),

  // Research
  getResearch: (openingId: string) => apiRequest<ORResearch[]>(`${base(openingId)}/research`),
  createResearch: (openingId: string, data: Omit<ORResearch, 'id' | 'resume_id'>) =>
    apiRequest<ORResearch>(`${base(openingId)}/research`, { method: 'POST', body: data }),
  updateResearch: (openingId: string, itemId: string, data: Partial<Omit<ORResearch, 'id' | 'resume_id'>>) =>
    apiRequest<ORResearch>(`${base(openingId)}/research/${itemId}`, { method: 'PATCH', body: data }),
  deleteResearch: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/research/${itemId}`, { method: 'DELETE' }),

  // Certifications
  getCertifications: (openingId: string) => apiRequest<ORCertification[]>(`${base(openingId)}/certifications`),
  createCertification: (openingId: string, data: Omit<ORCertification, 'id' | 'resume_id'>) =>
    apiRequest<ORCertification>(`${base(openingId)}/certifications`, { method: 'POST', body: data }),
  updateCertification: (openingId: string, itemId: string, data: Partial<Omit<ORCertification, 'id' | 'resume_id'>>) =>
    apiRequest<ORCertification>(`${base(openingId)}/certifications/${itemId}`, { method: 'PATCH', body: data }),
  deleteCertification: (openingId: string, itemId: string) =>
    apiRequest<void>(`${base(openingId)}/certifications/${itemId}`, { method: 'DELETE' }),

  // Skills (PUT replace-all for snapshots)
  getSkills: (openingId: string) => apiRequest<ORSkills>(`${base(openingId)}/skills`),
  updateSkills: (openingId: string, skills: string[]) =>
    apiRequest<ORSkills>(`${base(openingId)}/skills`, { method: 'PUT', body: { skills } }),
}
