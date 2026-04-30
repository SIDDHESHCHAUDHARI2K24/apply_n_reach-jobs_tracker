import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { AuthProvider } from '@core/auth/context'

interface WrapperProps {
  children: React.ReactNode
}

function Wrapper({ children }: WrapperProps) {
  return (
    <AuthProvider>{children}</AuthProvider>
  )
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  const rest = options ?? {}
  return render(ui, {
    wrapper: ({ children }) => <Wrapper>{children}</Wrapper>,
    ...rest,
  })
}
