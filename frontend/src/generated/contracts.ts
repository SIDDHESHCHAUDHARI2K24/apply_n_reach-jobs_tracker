import type { components } from './schema'

export type ApiSchemas = components['schemas']

export type UserProfilePersonalResponse = ApiSchemas['PersonalDetailsResponse']
export type UserProfilePersonalUpdate = ApiSchemas['PersonalDetailsUpdate']
export type UserProfileEducationResponse =
  ApiSchemas['app__features__user_profile__education__schemas__EducationResponse']
export type UserProfileEducationCreate =
  ApiSchemas['app__features__user_profile__education__schemas__EducationCreate']
export type UserProfileEducationUpdate =
  ApiSchemas['app__features__user_profile__education__schemas__EducationUpdate']
export type UserProfileExperienceResponse =
  ApiSchemas['app__features__user_profile__experience__schemas__ExperienceResponse']
export type UserProfileExperienceCreate =
  ApiSchemas['app__features__user_profile__experience__schemas__ExperienceCreate']
export type UserProfileExperienceUpdate =
  ApiSchemas['app__features__user_profile__experience__schemas__ExperienceUpdate']
export type UserProfileProjectResponse =
  ApiSchemas['app__features__user_profile__projects__schemas__ProjectResponse']
export type UserProfileProjectCreate =
  ApiSchemas['app__features__user_profile__projects__schemas__ProjectCreate']
export type UserProfileProjectUpdate =
  ApiSchemas['app__features__user_profile__projects__schemas__ProjectUpdate']
export type UserProfileResearchResponse =
  ApiSchemas['app__features__user_profile__research__schemas__ResearchResponse']
export type UserProfileResearchCreate =
  ApiSchemas['app__features__user_profile__research__schemas__ResearchCreate']
export type UserProfileResearchUpdate =
  ApiSchemas['app__features__user_profile__research__schemas__ResearchUpdate']
export type UserProfileCertificationResponse =
  ApiSchemas['app__features__user_profile__certifications__schemas__CertificationResponse']
export type UserProfileCertificationCreate =
  ApiSchemas['app__features__user_profile__certifications__schemas__CertificationCreate']
export type UserProfileCertificationUpdate =
  ApiSchemas['app__features__user_profile__certifications__schemas__CertificationUpdate']
export type UserProfileSkillItemResponse = ApiSchemas['SkillItemResponse']
export type UserProfileSkillsUpdate = ApiSchemas['SkillsUpdate']

export type JobProfileResponse = ApiSchemas['JobProfileResponse']
export type JobProfileCreate = ApiSchemas['JobProfileCreate']
export type PaginatedJobProfileResponse = ApiSchemas['PaginatedResponse_JobProfileResponse_']
export type JobProfilePersonalResponse = ApiSchemas['JPPersonalDetailsResponse']
export type JobProfilePersonalUpdate = ApiSchemas['JPPersonalDetailsUpdate']
export type JobProfileEducationResponse = ApiSchemas['JPEducationResponse']
export type JobProfileEducationCreate = ApiSchemas['JPEducationCreate']
export type JobProfileEducationUpdate = ApiSchemas['JPEducationUpdate']
export type JobProfileExperienceResponse = ApiSchemas['JPExperienceResponse']
export type JobProfileExperienceCreate = ApiSchemas['JPExperienceCreate']
export type JobProfileExperienceUpdate = ApiSchemas['JPExperienceUpdate']
export type JobProfileProjectResponse = ApiSchemas['JPProjectResponse']
export type JobProfileProjectCreate = ApiSchemas['JPProjectCreate']
export type JobProfileProjectUpdate = ApiSchemas['JPProjectUpdate']
export type JobProfileResearchResponse = ApiSchemas['JPResearchResponse']
export type JobProfileResearchCreate = ApiSchemas['JPResearchCreate']
export type JobProfileResearchUpdate = ApiSchemas['JPResearchUpdate']
export type JobProfileCertificationResponse = ApiSchemas['JPCertificationResponse']
export type JobProfileCertificationCreate = ApiSchemas['JPCertificationCreate']
export type JobProfileCertificationUpdate = ApiSchemas['JPCertificationUpdate']
export type JobProfileSkillItemResponse = ApiSchemas['JPSkillItemResponse']
export type JobProfileSkillsUpdate = ApiSchemas['JPSkillsUpdate']

export type OpeningResumeResponse = ApiSchemas['ResumeResponse']
export type OpeningResumePersonalResponse = ApiSchemas['PersonalResponse']
export type OpeningResumePersonalUpdate = ApiSchemas['PersonalUpdate']
export type OpeningResumeEducationResponse =
  ApiSchemas['app__features__job_tracker__opening_resume__education__schemas__EducationResponse']
export type OpeningResumeEducationCreate =
  ApiSchemas['app__features__job_tracker__opening_resume__education__schemas__EducationCreate']
export type OpeningResumeEducationUpdate =
  ApiSchemas['app__features__job_tracker__opening_resume__education__schemas__EducationUpdate']
export type OpeningResumeExperienceResponse =
  ApiSchemas['app__features__job_tracker__opening_resume__experience__schemas__ExperienceResponse']
export type OpeningResumeExperienceCreate =
  ApiSchemas['app__features__job_tracker__opening_resume__experience__schemas__ExperienceCreate']
export type OpeningResumeExperienceUpdate =
  ApiSchemas['app__features__job_tracker__opening_resume__experience__schemas__ExperienceUpdate']
export type OpeningResumeProjectResponse =
  ApiSchemas['app__features__job_tracker__opening_resume__projects__schemas__ProjectResponse']
export type OpeningResumeProjectCreate =
  ApiSchemas['app__features__job_tracker__opening_resume__projects__schemas__ProjectCreate']
export type OpeningResumeProjectUpdate =
  ApiSchemas['app__features__job_tracker__opening_resume__projects__schemas__ProjectUpdate']
export type OpeningResumeResearchResponse =
  ApiSchemas['app__features__job_tracker__opening_resume__research__schemas__ResearchResponse']
export type OpeningResumeResearchCreate =
  ApiSchemas['app__features__job_tracker__opening_resume__research__schemas__ResearchCreate']
export type OpeningResumeResearchUpdate =
  ApiSchemas['app__features__job_tracker__opening_resume__research__schemas__ResearchUpdate']
export type OpeningResumeCertificationResponse =
  ApiSchemas['app__features__job_tracker__opening_resume__certifications__schemas__CertificationResponse']
export type OpeningResumeCertificationCreate =
  ApiSchemas['app__features__job_tracker__opening_resume__certifications__schemas__CertificationCreate']
export type OpeningResumeCertificationUpdate =
  ApiSchemas['app__features__job_tracker__opening_resume__certifications__schemas__CertificationUpdate']
export type OpeningResumeSkillResponse = ApiSchemas['SkillResponse']
export type OpeningResumeSkillCreate = ApiSchemas['SkillCreate']
export type OpeningResumeSkillUpdate = ApiSchemas['SkillUpdate']

export type JobOpeningResponse = ApiSchemas['OpeningResponse']
export type JobOpeningCreate = ApiSchemas['OpeningCreate']
export type JobOpeningUpdate = ApiSchemas['OpeningUpdate']
export type JobOpeningListResponse = ApiSchemas['OpeningListResponse']
export type JobOpeningStatus = ApiSchemas['OpeningStatus']
export type JobOpeningStatusTransitionRequest = ApiSchemas['StatusTransitionRequest']
export type JobOpeningStatusHistoryEntry = ApiSchemas['StatusHistoryEntry']
export type ExtractionRunResponse = ApiSchemas['ExtractionRunResponse']
export type ExtractedDetailsResponse = ApiSchemas['ExtractedDetailsResponse']
export type ManualExtractedDetailsCreate = ApiSchemas['ManualExtractedDetailsCreate']

export type RenderedOpeningResumeResponse = ApiSchemas['RenderedOpeningResumeResponse']
export type OpeningResumeRenderRequest = ApiSchemas['app__features__job_tracker__opening_resume__latex_resume__schemas__RenderResumeRequest']
