import React, { useState } from 'react'
import { Link } from 'react-router-dom'
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
    <form onSubmit={handleSubmit} noValidate>
      <h1>Reset password</h1>
      {displayError && <div role="alert" style={{ color: 'red', marginBottom: '1rem' }}>{displayError}</div>}
      {success && <div role="status" style={{ color: 'green', marginBottom: '1rem' }}>{success}</div>}
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email" />
      </div>
      <div>
        <label htmlFor="new-password">New password</label>
        <input id="new-password" type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required autoComplete="new-password" />
      </div>
      <button type="submit" disabled={isLoading}>{isLoading ? 'Resetting…' : 'Reset password'}</button>
      <p><Link to="/auth/login">Back to sign in</Link></p>
    </form>
  )
}
