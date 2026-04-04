// src/steps/Step1JobDescription.jsx
import { useRef, useState } from 'react'

const ACCEPTED = '.pdf,.docx,.txt'

function FileUploadField({ label, hint, placeholder, value, onChange, fieldKey }) {
  const inputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [uploadedName, setUploadedName] = useState(null)

  const handleFile = async (file) => {
    if (!file) return
    setUploading(true)
    setUploadError(null)
    setUploadedName(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/extract-text', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        setUploadError(data.detail || 'Failed to extract text from file.')
        return
      }
      onChange({ [fieldKey]: data.text })
      setUploadedName(data.filename)
    } catch (err) {
      setUploadError('Upload failed — is the backend running?')
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleDragOver = (e) => e.preventDefault()

  const clearFile = () => {
    setUploadedName(null)
    setUploadError(null)
    onChange({ [fieldKey]: '' })
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      <p className="text-xs text-slate-400 mb-2">{hint}</p>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => inputRef.current?.click()}
        className="mb-2 flex items-center justify-between gap-3 px-4 py-3 border-2
                   border-dashed border-slate-200 rounded-lg cursor-pointer
                   hover:border-indigo-300 hover:bg-indigo-50 transition-all group"
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          className="hidden"
          onChange={e => handleFile(e.target.files[0])}
        />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-slate-100 group-hover:bg-indigo-100
                          flex items-center justify-center flex-shrink-0 transition-colors">
            {uploading ? (
              <svg className="animate-spin w-4 h-4 text-indigo-500" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10"
                        stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
            ) : uploadedName ? (
              <svg className="w-4 h-4 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0
                     01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0
                     011.414 0z" clipRule="evenodd"/>
              </svg>
            ) : (
              <svg className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition-colors"
                   viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0
                     01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1
                     0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1
                     0 01-1.414 0z" clipRule="evenodd"/>
              </svg>
            )}
          </div>

          <div>
            {uploading && (
              <p className="text-xs text-indigo-600 font-medium">Extracting text…</p>
            )}
            {!uploading && uploadedName && (
              <p className="text-xs text-green-600 font-medium">
                {uploadedName} — text extracted
              </p>
            )}
            {!uploading && !uploadedName && (
              <p className="text-xs text-slate-500 group-hover:text-indigo-600 transition-colors">
                Drop file here or click to browse
              </p>
            )}
            <p className="text-xs text-slate-400">PDF · DOCX · TXT</p>
          </div>
        </div>

        {uploadedName && (
          <button
            onClick={e => { e.stopPropagation(); clearFile() }}
            className="text-xs text-slate-400 hover:text-red-500 transition-colors px-2"
          >
            clear
          </button>
        )}
      </div>

      {/* Upload error */}
      {uploadError && (
        <p className="text-xs text-red-500 mb-2">⚠ {uploadError}</p>
      )}

      {/* Text area — always visible, auto-populated on upload or manual paste */}
      <textarea
        className="w-full h-44 px-3 py-2 text-sm border border-slate-200 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none
                   bg-white placeholder-slate-300"
        placeholder={placeholder}
        value={value}
        onChange={e => {
          setUploadedName(null)
          onChange({ [fieldKey]: e.target.value })
        }}
      />
      {value && (
        <p className="text-xs text-slate-400 mt-1 text-right">
          {value.trim().split(/\s+/).filter(Boolean).length} words
        </p>
      )}
    </div>
  )
}

export default function Step1JobDescription({ data, onChange }) {
  return (
    <div className="space-y-6">
      <FileUploadField
        label="Job description"
        hint="Upload a PDF, DOCX, or TXT file — or paste the text directly below."
        placeholder={"Senior ML Engineer — Stripe\n\nWe're looking for a Senior ML Engineer to join our Risk & Fraud team..."}
        value={data.jobDescription}
        onChange={onChange}
        fieldKey="jobDescription"
      />
      <FileUploadField
        label="Your resume"
        hint="Upload your resume file — or paste the text directly below."
        placeholder={"Alex Rivera — Senior ML Engineer\n\nEXPERIENCE\nML Engineer, DataCo (2021–present)..."}
        value={data.resume}
        onChange={onChange}
        fieldKey="resume"
      />
    </div>
  )
}
