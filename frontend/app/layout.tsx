import type { Metadata } from 'next'
import type { CSSProperties, ReactNode } from 'react'
import { DM_Sans, Sora } from 'next/font/google'
import '../src/index.css'
import { AppProviders } from '../src/next/AppProviders'

const dmSans = DM_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
})

const sora = Sora({
  subsets: ['latin'],
  weight: ['600', '700'],
})

export const metadata: Metadata = {
  title: 'apply_n_reach',
  description: 'Job tracking and profile management dashboard',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={
          {
            '--font-ui': dmSans.style.fontFamily,
            '--font-heading': sora.style.fontFamily,
          } as CSSProperties
        }
      >
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  )
}
