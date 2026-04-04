// src/steps/Step5Export.jsx
import { useState } from 'react'

const STATUS_OPTIONS = ['drafted', 'copied', 'sent', 'followup_due', 'replied']

const STATUS_COLORS = {
  drafted:      'bg-slate-100 text-slate-600',
  copied:       'bg-blue-100 text-blue-700',
  sent:         'bg-indigo-100 text-indigo-700',
  followup_due: 'bg-amber-100 text-amber-700',
  replied:      'bg-green-100 text-green-700',
}

export default function Step5Export({ finalResult, editedBody, selectedSubject, threadId }) {
  const [status, setStatus] = useState(finalResult?.status || 'drafted')
  const [copied, setCopied] = useState(false)
  const [copiedSubject, setCopiedSubject] = useState(false)

  // Send via Resend
  const [sendTo, setSendTo] = useState(finalResult?.contact_email || '')
  const [sending, setSending] = useState(false)
  const [sendResult, setSendResult] = useState(null)  // {success, message}

  const emailBody = finalResult?.email_body || editedBody || ''
  const subject = selectedSubject
  const contactEmail = finalResult?.contact_email

  const copyBody = async () => {
    await navigator.clipboard.writeText(emailBody)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    if (status === 'drafted') setStatus('copied')
  }

  const copySubject = async () => {
    await navigator.clipboard.writeText(subject)
    setCopiedSubject(true)
    setTimeout(() => setCopiedSubject(false), 2000)
  }

  const exportTxt = () => {
    const content = `Subject: ${subject}\n\n${emailBody}`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `outreach-email-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const openMailto = () => {
    const to = contactEmail || ''
    const url = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`
    window.open(url)
    setStatus('copied')
  }

  const sendViaResend = async () => {
    if (!sendTo || !sendTo.includes('@')) {
      setSendResult({ success: false, message: 'Please enter a valid email address.' })
      return
    }
    setSending(true)
    setSendResult(null)
    try {
      const res = await fetch('/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: threadId,
          to_email: sendTo,
          subject,
          body: emailBody,
        }),
      })
      const data = await res.json()
      setSendResult(data)
      if (data.success) setStatus('sent')
    } catch (err) {
      setSendResult({ success: false, message: err.message })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-5">

      {/* Status tracker */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Outreach status
        </label>
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map(s => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all font-medium
                ${status === s
                  ? `${STATUS_COLORS[s]} border-transparent`
                  : 'border-slate-200 text-slate-400 hover:border-slate-300'
                }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
        {status === 'followup_due' && (
          <p className="text-xs text-amber-600 mt-2">
            Time to send your follow-up — the draft is in step 4.
          </p>
        )}
        {status === 'replied' && (
          <p className="text-xs text-green-600 mt-2">
            Great work! Mark the next steps in your job search tracker.
          </p>
        )}
      </div>

      {/* Subject line */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 px-4 py-3">
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs font-medium text-slate-500">Subject line</p>
          <button onClick={copySubject} className="text-xs text-indigo-500 hover:text-indigo-700">
            {copiedSubject ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <p className="text-sm text-slate-700">{subject}</p>
      </div>

      {/* Email body preview */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-slate-700">Email body</p>
          <span className="text-xs text-slate-400">
            {emailBody.trim().split(/\s+/).filter(Boolean).length} words
          </span>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg px-4 py-3 text-sm
                        text-slate-700 leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
          {emailBody}
        </div>
      </div>

      {/* Send via Resend */}
      <div className="border border-slate-200 rounded-xl p-4 space-y-3">
        <p className="text-sm font-medium text-slate-700">Send via Resend</p>
        <div className="flex gap-2">
          <input
            type="email"
            placeholder="recipient@company.com"
            value={sendTo}
            onChange={e => setSendTo(e.target.value)}
            className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
          />
          <button
            onClick={sendViaResend}
            disabled={sending}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm
                       font-medium rounded-lg transition-colors disabled:opacity-40
                       disabled:cursor-not-allowed whitespace-nowrap"
          >
            {sending ? 'Sending…' : 'Send now'}
          </button>
        </div>
        {sendResult && (
          <p className={`text-xs ${sendResult.success ? 'text-green-600' : 'text-red-500'}`}>
            {sendResult.success ? '✓' : '✗'} {sendResult.message}
          </p>
        )}
        <p className="text-xs text-slate-400">
          Powered by Resend — requires RESEND_API_KEY in your .env
        </p>
      </div>

      {/* Other actions */}
      <div className="grid grid-cols-1 gap-2">
        <button
          onClick={copyBody}
          className="w-full py-2.5 bg-white hover:bg-slate-50 text-slate-700 text-sm
                     font-medium rounded-lg border border-slate-200 transition-colors"
        >
          {copied ? 'Copied to clipboard!' : 'Copy email body'}
        </button>

        {contactEmail && (
          <button
            onClick={openMailto}
            className="w-full py-2.5 bg-white hover:bg-slate-50 text-slate-600 text-sm
                       rounded-lg border border-slate-200 transition-colors"
          >
            Open in mail app → {contactEmail}
          </button>
        )}

        <button
          onClick={exportTxt}
          className="w-full py-2.5 bg-white hover:bg-slate-50 text-slate-500 text-sm
                     rounded-lg border border-slate-200 transition-colors"
        >
          Export as .txt
        </button>
      </div>

      {/* Thread ID */}
      {finalResult?.thread_id && (
        <p className="text-xs text-slate-300 text-center">
          Thread: {finalResult.thread_id}
        </p>
      )}
    </div>
  )
}

const STATUS_OPTIONS = ['drafted', 'copied', 'sent', 'followup_due', 'replied']

const STATUS_COLORS = {
  drafted:      'bg-slate-100 text-slate-600',
  copied:       'bg-blue-100 text-blue-700',
  sent:         'bg-indigo-100 text-indigo-700',
  followup_due: 'bg-amber-100 text-amber-700',
  replied:      'bg-green-100 text-green-700',
}

export default function Step5Export({ finalResult, editedBody, selectedSubject }) {
  const [status, setStatus] = useState(finalResult?.status || 'drafted')
  const [copied, setCopied] = useState(false)
  const [copiedSubject, setCopiedSubject] = useState(false)

  const emailBody = finalResult?.email_body || editedBody || ''
  const subject = finalResult ? selectedSubject : selectedSubject
  const contactEmail = finalResult?.contact_email

  const copyBody = async () => {
    await navigator.clipboard.writeText(emailBody)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    if (status === 'drafted') setStatus('copied')
  }

  const copySubject = async () => {
    await navigator.clipboard.writeText(subject)
    setCopiedSubject(true)
    setTimeout(() => setCopiedSubject(false), 2000)
  }

  const exportTxt = () => {
    const content = `Subject: ${subject}\n\n${emailBody}`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `outreach-email-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const openMailto = () => {
    const to = contactEmail || ''
    const url = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`
    window.open(url)
    setStatus('copied')
  }

  return (
    <div className="space-y-5">

      {/* Status tracker */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Outreach status
        </label>
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map(s => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all font-medium
                ${status === s
                  ? `${STATUS_COLORS[s]} border-transparent`
                  : 'border-slate-200 text-slate-400 hover:border-slate-300'
                }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
        {status === 'followup_due' && (
          <p className="text-xs text-amber-600 mt-2">
            Time to send your follow-up — the draft is in step 4.
          </p>
        )}
        {status === 'replied' && (
          <p className="text-xs text-green-600 mt-2">
            Great work! Mark the next steps in your job search tracker.
          </p>
        )}
      </div>

      {/* Subject line */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 px-4 py-3">
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs font-medium text-slate-500">Subject line</p>
          <button
            onClick={copySubject}
            className="text-xs text-indigo-500 hover:text-indigo-700"
          >
            {copiedSubject ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <p className="text-sm text-slate-700">{subject}</p>
      </div>

      {/* Email body preview */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-slate-700">Email body</p>
          <span className="text-xs text-slate-400">
            {emailBody.trim().split(/\s+/).filter(Boolean).length} words
          </span>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg px-4 py-3 text-sm
                        text-slate-700 leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
          {emailBody}
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 gap-2">
        <button
          onClick={copyBody}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm
                     font-medium rounded-lg transition-colors"
        >
          {copied ? 'Copied to clipboard!' : 'Copy email body'}
        </button>

        {contactEmail && (
          <button
            onClick={openMailto}
            className="w-full py-3 bg-white hover:bg-slate-50 text-slate-700 text-sm
                       font-medium rounded-lg border border-slate-200 transition-colors"
          >
            Open in mail app → {contactEmail}
          </button>
        )}

        <button
          onClick={exportTxt}
          className="w-full py-2.5 bg-white hover:bg-slate-50 text-slate-600 text-sm
                     rounded-lg border border-slate-200 transition-colors"
        >
          Export as .txt
        </button>
      </div>

      {/* Thread ID for reference */}
      {finalResult?.thread_id && (
        <p className="text-xs text-slate-300 text-center">
          Thread: {finalResult.thread_id}
        </p>
      )}
    </div>
  )
}
