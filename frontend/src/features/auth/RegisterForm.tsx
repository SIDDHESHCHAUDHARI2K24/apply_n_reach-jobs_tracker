import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useRegisterForm } from './useAuthForms'

export function RegisterForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  const { register, isLoading, error } = useRegisterForm()

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
    await register({ email: email.trim(), password })
  }

  const displayError = validationError ?? error

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h1>Create account</h1>
      {displayError && <div role="alert" style={{ color: 'red', marginBottom: '1rem' }}>{displayError}</div>}
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email" />
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} required autoComplete="new-password" />
      </div>
      <button type="submit" disabled={isLoading}>{isLoading ? 'Creating account…' : 'Create account'}</button>
      <p><Link to="/auth/login">Already have an account?</Link></p>
    </form>
  )
}
