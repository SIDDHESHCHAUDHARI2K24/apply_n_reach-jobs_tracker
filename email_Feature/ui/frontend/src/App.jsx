// src/App.jsx
import { useState } from 'react'
import { generateEmail, resumeAfterReview } from './api'
import Step1JobDescription from './steps/Step1JobDescription'
import Step2RecipientType from './steps/Step2RecipientType'
import Step3LinkedIn from './steps/Step3LinkedIn'
import Step4Review from './steps/Step4Review'
import Step5Export from './steps/Step5Export'

const STEPS = [
  { id: 1, label: 'Job & resume' },
  { id: 2, label: 'Recipient' },
  { id: 3, label: 'LinkedIn' },
  { id: 4, label: 'Review' },
  { id: 5, label: 'Export' },
]

const INITIAL_FORM = {
  jobDescription: '',
  resume: '',
  recipientType: 'recruiter',
  linkedinPaste: '',
  contactNameOverride: '',
}

const INITIAL_EDITED = {
  editedBody: null,
  selectedSubject: '',
  resetToAi: false,
}

export default function App() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState(INITIAL_FORM)
  const [edited, setEdited] = useState(INITIAL_EDITED)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [generateResult, setGenerateResult] = useState(null)
  const [finalResult, setFinalResult] = useState(null)

  const updateForm = (patch) => setForm(f => ({ ...f, ...patch }))
  const updateEdited = (patch) => setEdited(e => ({ ...e, ...patch }))

  // Validation per step
  const canAdvance = () => {
    if (step === 1) return form.jobDescription.trim().length > 20 && form.resume.trim().length > 20
    if (step === 2) return !!form.recipientType
    if (step === 3) return true  // optional step
    if (step === 4) return !!generateResult
    return false
  }

  const handleNext = async () => {
    setError(null)

    // Step 3 → 4: trigger API call
    if (step === 3) {
      setLoading(true)
      try {
        const result = await generateEmail({
          jobDescription: form.jobDescription,
          resume: form.resume,
          recipientType: form.recipientType,
          linkedinPaste: form.linkedinPaste,
          contactNameOverride: form.contactNameOverride,
        })
        setGenerateResult(result)
        setEdited({
          editedBody: result.email_body,
          selectedSubject: result.subject_options[0] || '',
          resetToAi: false,
        })
        setStep(4)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
      return
    }

    // Step 4 → 5: resume graph after review
    if (step === 4) {
      setLoading(true)
      try {
        const result = await resumeAfterReview({
          threadId: generateResult.thread_id,
          editedBody: edited.editedBody ?? generateResult.email_body,
          selectedSubject: edited.selectedSubject || generateResult.subject_options[0],
          resetToAi: edited.resetToAi || false,
        })
        setFinalResult(result)
        setStep(5)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
      return
    }

    setStep(s => Math.min(s + 1, 5))
  }

  const handleBack = () => {
    setError(null)
    setStep(s => Math.max(s - 1, 1))
  }

  const handleReset = () => {
    setStep(1)
    setForm(INITIAL_FORM)
    setEdited(INITIAL_EDITED)
    setGenerateResult(null)
    setFinalResult(null)
    setError(null)
  }

  const nextLabel = () => {
    if (step === 3) return loading ? 'Generating…' : 'Generate email'
    if (step === 4) return loading ? 'Finalizing…' : 'Confirm & finalize'
    if (step === 5) return null
    return 'Continue'
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center py-10 px-4">

      {/* Header */}
      <div className="w-full max-w-xl mb-8">
        <h1 className="text-2xl font-semibold text-slate-800 mb-1">
          AI Outreach Email Assistant
        </h1>
        <p className="text-sm text-slate-400">
          Generate a personalized outreach email from your resume and a job description.
        </p>
      </div>

      {/* Progress indicator */}
      <div className="w-full max-w-xl mb-6">
        <div className="flex items-center gap-0">
          {STEPS.map((s, i) => (
            <div key={s.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold
                  transition-colors
                  ${step > s.id
                    ? 'bg-indigo-600 text-white'
                    : step === s.id
                      ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-500'
                      : 'bg-slate-200 text-slate-400'
                  }`}>
                  {step > s.id ? '✓' : s.id}
                </div>
                <span className={`text-xs mt-1 whitespace-nowrap
                  ${step === s.id ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-1 mb-4
                  ${step > s.id ? 'bg-indigo-400' : 'bg-slate-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Card */}
      <div className="w-full max-w-xl bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">

        {/* Step title */}
        <div className="px-6 pt-6 pb-4 border-b border-slate-100">
          <h2 className="text-base font-semibold text-slate-800">
            {step === 1 && 'Paste your job description and resume'}
            {step === 2 && 'Who are you reaching out to?'}
            {step === 3 && 'Add LinkedIn context (optional)'}
            {step === 4 && 'Review and edit your email'}
            {step === 5 && 'Your email is ready'}
          </h2>
        </div>

        {/* Step content */}
        <div className="px-6 py-5">
          {step === 1 && <Step1JobDescription data={form} onChange={updateForm} />}
          {step === 2 && <Step2RecipientType data={form} onChange={updateForm} />}
          {step === 3 && <Step3LinkedIn data={form} onChange={updateForm} />}
          {step === 4 && (
            <Step4Review
              result={generateResult}
              edited={edited}
              onChange={updateEdited}
            />
          )}
          {step === 5 && (
            <Step5Export
              finalResult={finalResult}
              editedBody={edited.editedBody}
              selectedSubject={edited.selectedSubject}
              threadId={generateResult?.thread_id}
              recipientType={form.recipientType}
              contactName={generateResult?.contact_name}
              contactEmail={generateResult?.contact_email}
            />
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mx-6 mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="px-6 pb-6 flex items-center justify-between gap-3">
          <div>
            {step > 1 && step < 5 && (
              <button
                onClick={handleBack}
                disabled={loading}
                className="text-sm text-slate-500 hover:text-slate-700 disabled:opacity-40"
              >
                ← Back
              </button>
            )}
            {step === 5 && (
              <button
                onClick={handleReset}
                className="text-sm text-slate-500 hover:text-slate-700"
              >
                ← Start over
              </button>
            )}
          </div>

          {nextLabel() && (
            <button
              onClick={handleNext}
              disabled={!canAdvance() || loading}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm
                         font-medium rounded-lg transition-colors disabled:opacity-40
                         disabled:cursor-not-allowed min-w-36 text-center"
            >
              {nextLabel()}
            </button>
          )}
        </div>
      </div>

      {/* Footer note */}
      <p className="mt-6 text-xs text-slate-300 text-center max-w-sm">
        Academic prototype — AI Systems Capstone, Group 1 · 2026
      </p>
    </div>
  )
}
