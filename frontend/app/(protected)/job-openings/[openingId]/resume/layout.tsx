import type { ReactNode } from 'react'
import { OpeningResumeShell } from '../../../../../src/features/opening-resume/shell/OpeningResumeShell'

interface LayoutProps {
  children: ReactNode
  params: Promise<{ openingId: string }>
}

export default async function OpeningResumeLayout({ children, params }: LayoutProps) {
  const { openingId } = await params
  return <OpeningResumeShell openingId={openingId}>{children}</OpeningResumeShell>
}
