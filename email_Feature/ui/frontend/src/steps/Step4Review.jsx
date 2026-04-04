// src/steps/Step4Review.jsx
import { useState } from 'react'

export default function Step4Review({ result, edited, onChange }) {
  const [activeSubject, setActiveSubject] = useState(0)
  const [showFollowup, setShowFollowup] = useState(false)

  if (!result) return null

  const {
    email_body,
    subject_options,
    followup_body,
    followup_days,
    contact_name,
    contact_email,
    contact_title,
    apollo_found,
    personalization_signals,
    warnings,
    word_count,
  } = result

  const selectedSubject = subject_options[activeSubject] || ''

  // Keep parent in sync with subject selection
  const handleSubjectSelect = (idx) => {
    setActiveSubject(idx)
    onChange({ selectedSubject: subject_options[idx] })
  }

  const handleBodyChange = (e) => {
    onChange({ editedBody: e.target.value })
  }

  const handleReset = () => {
    onChange({ editedBody: email_body, resetToAi: true })
  }

  const currentBody = edited.editedBody ?? email_body
  const currentWordCount = currentBody.trim().split(/\s+/).filter(Boolean).length

  return (
    <div className="space-y-5">

      {/* Contact info banner */}
      {apollo_found && contact_name ? (
        <div className="flex items-start gap-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3">
          <div className="w-8 h-8 rounded-full bg-green-200 flex items-center justify-center text-green-800 font-semibold text-xs flex-shrink-0 mt-0.5">
            {contact_name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase()}
          </div>
          <div>
            <p className="text-sm font-medium text-green-800">{contact_name}</p>
            {contact_title && <p className="text-xs text-green-700">{contact_title}</p>}
            {contact_email
              ? <p className="text-xs text-green-600 mt-0.5">Verified email found: {contact_email}</p>
              : <p className="text-xs text-amber-600 mt-0.5">No verified email — use LinkedIn message instead</p>
            }
          </div>
        </div>
      ) : (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
          <p className="text-sm text-amber-800">
            No contact found via Apollo — email is ready but you'll need to find the address manually or send via LinkedIn.
          </p>
        </div>
      )}

      {/* Subject line selector */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Subject line
        </label>
        <div className="space-y-2">
          {subject_options.map((opt, i) => (
            <button
              key={i}
              onClick={() => handleSubjectSelect(i)}
              className={`w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-all
                ${i === activeSubject
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-800 font-medium'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      {/* Email body editor */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-slate-700">
            Email body
          </label>
          <div className="flex items-center gap-3">
            <span className={`text-xs ${currentWordCount > 250 ? 'text-red-500' : 'text-slate-400'}`}>
              {currentWordCount} words
            </span>
            {currentBody !== email_body && (
              <button
                onClick={handleReset}
                className="text-xs text-indigo-500 hover:text-indigo-700 underline underline-offset-2"
              >
                Reset to AI version
              </button>
            )}
          </div>
        </div>
        <textarea
          className="w-full h-72 px-3 py-2 text-sm border border-slate-200 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none
                     bg-white leading-relaxed"
          value={currentBody}
          onChange={handleBodyChange}
        />
      </div>

      {/* Personalization signals */}
      {personalization_signals.length > 0 && (
        <div>
          <p className="text-xs font-medium text-slate-500 mb-2">Personalization applied</p>
          <div className="flex flex-wrap gap-1.5">
            {personalization_signals.map((sig, i) => (
              <span
                key={i}
                className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full"
              >
                {sig}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Follow-up draft toggle */}
      <div className="border border-slate-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setShowFollowup(v => !v)}
          className="w-full flex items-center justify-between px-4 py-3 bg-slate-50
                     hover:bg-slate-100 transition-colors text-sm font-medium text-slate-700"
        >
          <span>Follow-up draft (send after {followup_days} days)</span>
          <span className="text-slate-400 text-xs">{showFollowup ? 'hide' : 'show'}</span>
        </button>
        {showFollowup && followup_body && (
          <div className="px-4 py-3 text-sm text-slate-600 leading-relaxed whitespace-pre-wrap bg-white">
            {followup_body}
          </div>
        )}
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <p key={i} className="text-xs text-amber-600 flex gap-1.5">
              <span>⚠</span><span>{w}</span>
            </p>
          ))}
        </div>
      )}
    </div>
  )
}
