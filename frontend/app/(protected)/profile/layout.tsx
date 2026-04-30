import type { ReactNode } from 'react'
import { ProfileShell } from '../../../src/features/user-profile/shell/ProfileShell'

export default function ProfileLayout({ children }: { children: ReactNode }) {
  return <ProfileShell>{children}</ProfileShell>
}
