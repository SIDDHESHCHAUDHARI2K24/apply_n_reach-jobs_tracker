'use client'

import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useAuth } from '@core/auth/context'
import { AppLayout } from '@app/layout/AppLayout'

export function ProtectedShell({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading && !user) {
      const returnTo = encodeURIComponent(pathname || '/job-profiles')
      router.replace(`/auth/login?returnTo=${returnTo}`)
    }
  }, [isLoading, user, pathname, router])

  if (isLoading) return <div>Loading...</div>
  if (!user) return <div>Loading...</div>

  return <AppLayout>{children}</AppLayout>
}
