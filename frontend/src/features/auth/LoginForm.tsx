'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { AlertCircle } from 'lucide-react'
import { useLoginForm } from './useAuthForms'

export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  const { login, isLoading, error } = useLoginForm()

  function validate(): boolean {
    if (!email.trim()) { setValidationError('Email is required'); return false }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setValidationError('Enter a valid email'); return false }
    if (!password) { setValidationError('Password is required'); return false }
    if (password.length < 8) { setValidationError('Password must be at least 8 characters'); return false }
    setValidationError(null)
    return true
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    await login({ email: email.trim(), password })
  }

  const displayError = validationError ?? error

  return (
    <form onSubmit={handleSubmit} noValidate className="bg-white rounded-xl shadow-sm p-8">
      <h1 className="font-sora text-2xl font-bold text-slate-900 mb-2">Sign in</h1>
      <p className="text-slate-500 text-sm mb-6">Welcome back — enter your details below.</p>

      {displayError && (
        <div
          role="alert"
          className="flex items-start gap-2 bg-red-50 text-red-600 text-sm rounded-lg px-4 py-3 mb-5"
        >
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <span>{displayError}</span>
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
        <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          autoComplete="current-password"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          placeholder="••••••••"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2.5 px-4 bg-sky-500 hover:bg-sky-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Signing in…' : 'Sign in'}
      </button>

      <p className="mt-5 text-center text-sm text-slate-500">
        <Link href="/auth/register" className="text-sky-600 hover:underline font-medium">
          Create account
        </Link>
        <span className="mx-2 text-slate-300">·</span>
        <Link href="/auth/reset" className="text-sky-600 hover:underline font-medium">
          Forgot password?
        </Link>
      </p>
    </form>
  )
}
