'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@core/auth/context'
import {
  LayoutDashboard,
  BriefcaseBusiness,
  UserCircle,
  Settings,
  Rocket,
  type LucideIcon,
} from 'lucide-react'

interface NavItem {
  to: string
  label: string
  Icon: LucideIcon
}

const NAV_ITEMS: NavItem[] = [
  { to: '/job-tracker', label: 'Job Tracker', Icon: LayoutDashboard },
  { to: '/job-profiles', label: 'Job Profiles', Icon: BriefcaseBusiness },
  { to: '/profile', label: 'Profile', Icon: UserCircle },
  { to: '/settings', label: 'Settings', Icon: Settings },
]

export function AppLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const pathname = usePathname()

  function isActive(to: string): boolean {
    return pathname === to || pathname.startsWith(to + '/')
  }

  return (
    <div className="app-shell">
      <nav aria-label="Main navigation" className="app-sidebar">
        <div className="app-brand">
          <Rocket size={20} color="#38bdf8" strokeWidth={2.5} />
          <span>apply_n_reach</span>
        </div>
        <ul role="list" className="app-nav-list">
          {NAV_ITEMS.map(({ to, label, Icon }) => {
            const active = isActive(to)
            return (
              <li key={to}>
                <Link
                  href={to}
                  aria-current={active ? 'page' : undefined}
                  className={active ? 'app-nav-link app-nav-link-active' : 'app-nav-link'}
                >
                  <span className="shrink-0"><Icon size={18} /></span>
                  {label}
                </Link>
              </li>
            )
          })}
        </ul>
        <div className="flex-1" />
        {user && (
          <div className="app-sidebar-user">
            <UserCircle size={18} color="#94a3b8" />
            <span className="text-[0.8125rem] text-[var(--sidebar-text)] overflow-hidden text-ellipsis whitespace-nowrap flex-1" title={user.email}>
              {user.email}
            </span>
          </div>
        )}
      </nav>
      <main className="app-main">
        {children}
      </main>
    </div>
  )
}
