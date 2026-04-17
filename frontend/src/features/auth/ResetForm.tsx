import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import { useResetForm } from './useAuthForms'

export function ResetForm() {
  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  const { reset, isLoading, error, success } = useResetForm()

  function validate(): boolean {
    if (!email.trim()) { setValidationError('Email is required'); return false }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setValidationError('Enter a valid email'); return false }
    if (!newPassword) { setValidationError('New password is required'); return false }
    if (newPassword.length < 8) { setValidationError('Password must be at least 8 characters'); return false }
    setValidationError(null)
    return true
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    await reset({ email: email.trim(), new_password: newPassword })
  }

  const displayError = validationError ?? error

  return (
    <form onSubmit={handleSubmit} noValidate className="bg-white rounded-xl shadow-sm p-8">
      <h1 className="font-['Sora'] text-2xl font-bold text-slate-900 mb-2">Reset password</h1>
      <p className="text-slate-500 text-sm mb-6">Enter your email and a new password to regain access.</p>

      {displayError && (
        <div
          role="alert"
          className="flex items-start gap-2 bg-red-50 text-red-600 text-sm rounded-lg px-4 py-3 mb-5"
        >
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <span>{displayError}</span>
        </div>
      )}

      {success && (
        <div
          role="status"
          className="flex items-start gap-2 bg-green-50 text-green-600 text-sm rounded-lg px-4 py-3 mb-5"
        >
          <CheckCircle2 size={16} className="shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      <div className="mb-4">
        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          autoComplete="email"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          placeholder="you@example.com"
        />
      </div>

      <div className="mb-6">
        <label htmlFor="new-password" className="block text-sm font-medium text-slate-700 mb-1">
          New password
        </label>
        <input
          id="new-password"
          type="password"
          value={newPassword}
          onChange={e => setNewPassword(e.target.value)}
          required
          autoComplete="new-password"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          placeholder="Min. 8 characters"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2.5 px-4 bg-sky-500 hover:bg-sky-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Resetting…' : 'Reset password'}
      </button>

      <p className="mt-5 text-center text-sm text-slate-500">
        <Link to="/auth/login" className="text-sky-600 hover:underline font-medium">
          Back to sign in
        </Link>
      </p>
    </form>
  )
}
