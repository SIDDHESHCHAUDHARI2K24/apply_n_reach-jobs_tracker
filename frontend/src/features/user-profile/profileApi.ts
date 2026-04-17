import { apiRequest } from '@core/http/client'
import type {
  ProfileSummary,
  PersonalDetails,
  Education,
  Experience,
  Project,
  Research,
  Certification,
  SkillsData,
} from './types'

export const profileApi = {
  // Bootstrap
  bootstrapProfile: () =>
    apiRequest<ProfileSummary>('/profile', { method: 'POST' }),

  getProfileSummary: () =>
    apiRequest<ProfileSummary>('/profile/summary'),

  // Personal
  getPersonal: () =>
    apiRequest<PersonalDetails>('/profile/personal'),

  updatePersonal: (data: Partial<Omit<PersonalDetails, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<PersonalDetails>('/profile/personal', { method: 'PATCH', body: data }),

  // Education
  getEducation: () =>
    apiRequest<Education[]>('/profile/education'),

  createEducation: (data: Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) =>
    apiRequest<Education>('/profile/education', { method: 'POST', body: data }),

  updateEducation: (id: string, data: Partial<Omit<Education, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<Education>(`/profile/education/${id}`, { method: 'PATCH', body: data }),

  deleteEducation: (id: string) =>
    apiRequest<void>(`/profile/education/${id}`, { method: 'DELETE' }),

  // Experience
  getExperience: () =>
    apiRequest<Experience[]>('/profile/experience'),

  createExperience: (data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) =>
    apiRequest<Experience>('/profile/experience', { method: 'POST', body: data }),

  updateExperience: (id: string, data: Partial<Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<Experience>(`/profile/experience/${id}`, { method: 'PATCH', body: data }),

  deleteExperience: (id: string) =>
    apiRequest<void>(`/profile/experience/${id}`, { method: 'DELETE' }),

  // Projects
  getProjects: () =>
    apiRequest<Project[]>('/profile/projects'),

  createProject: (data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) =>
    apiRequest<Project>('/profile/projects', { method: 'POST', body: data }),

  updateProject: (id: string, data: Partial<Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<Project>(`/profile/projects/${id}`, { method: 'PATCH', body: data }),

  deleteProject: (id: string) =>
    apiRequest<void>(`/profile/projects/${id}`, { method: 'DELETE' }),

  // Research
  getResearch: () =>
    apiRequest<Research[]>('/profile/research'),

  createResearch: (data: Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) =>
    apiRequest<Research>('/profile/research', { method: 'POST', body: data }),

  updateResearch: (id: string, data: Partial<Omit<Research, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<Research>(`/profile/research/${id}`, { method: 'PATCH', body: data }),

  deleteResearch: (id: string) =>
    apiRequest<void>(`/profile/research/${id}`, { method: 'DELETE' }),

  // Certifications
  getCertifications: () =>
    apiRequest<Certification[]>('/profile/certifications'),

  createCertification: (data: Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) =>
    apiRequest<Certification>('/profile/certifications', { method: 'POST', body: data }),

  updateCertification: (id: string, data: Partial<Omit<Certification, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) =>
    apiRequest<Certification>(`/profile/certifications/${id}`, { method: 'PATCH', body: data }),

  deleteCertification: (id: string) =>
    apiRequest<void>(`/profile/certifications/${id}`, { method: 'DELETE' }),

  // Skills
  getSkills: () =>
    apiRequest<SkillsData>('/profile/skills'),

  updateSkills: (skills: string[]) =>
    apiRequest<SkillsData>('/profile/skills', { method: 'PATCH', body: { skills } }),
}
