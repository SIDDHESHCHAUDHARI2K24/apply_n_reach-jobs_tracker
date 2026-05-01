'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { User, LogOut } from 'lucide-react'
import { apiRequest } from '@core/http/client'
import { useAuth } from '@core/auth/context'

export function SettingsView() {
  const { user, clearUser } = useAuth()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const router = useRouter()

  const logout = useCallback(async () => {
    setIsLoggingOut(true)
    try {
      await apiRequest('/auth/logout', { method: 'POST' })
    } finally {
      clearUser()
      router.replace('/auth/login')
      setIsLoggingOut(false)
    }
  }, [router, clearUser])

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="font-sora text-2xl font-bold text-slate-800">Settings</h1>

      {/* Account card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2.5 px-5 py-4 border-b border-slate-100">
          <User size={16} className="text-slate-500" />
          <h2 className="font-sora text-sm font-semibold text-slate-700">Account</h2>
        </div>
        <div className="px-5 py-4">
          {user && (
            <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2.5 text-sm">
              <dt className="text-slate-500 font-medium">Email</dt>
              <dd className="text-slate-800">{user.email}</dd>
              <dt className="text-slate-500 font-medium">Member since</dt>
              <dd className="text-slate-800">{new Date(user.created_at).toLocaleDateString()}</dd>
            </dl>
          )}
        </div>
      </div>

      {/* Session card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2.5 px-5 py-4 border-b border-slate-100">
          <LogOut size={16} className="text-slate-500" />
          <h2 className="font-sora text-sm font-semibold text-slate-700">Session</h2>
        </div>
        <div className="px-5 py-4">
          <button
            onClick={logout}
            disabled={isLoggingOut}
            className="flex items-center justify-center gap-2 w-full bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            <LogOut size={15} />
            {isLoggingOut ? 'Signing out...' : 'Sign out'}
          </button>
        </div>
      </div>
    </div>
  )
}
