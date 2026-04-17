import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '@core/auth/context'

interface WrapperProps {
  children: React.ReactNode
  initialEntries?: string[]
}

function Wrapper({ children, initialEntries = ['/'] }: WrapperProps) {
  return (
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>{children}</AuthProvider>
    </MemoryRouter>
  )
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & { initialEntries?: string[] },
) {
  const { initialEntries, ...rest } = options ?? {}
  return render(ui, {
    wrapper: ({ children }) => <Wrapper initialEntries={initialEntries}>{children}</Wrapper>,
    ...rest,
  })
}
