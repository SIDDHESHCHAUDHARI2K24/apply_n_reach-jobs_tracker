import { vi } from 'vitest'

/**
 * Create a mock API module with vi.fn() stubs for all given function names.
 */
export function createApiMock<T extends string>(fnNames: T[]): Record<T, ReturnType<typeof vi.fn>> {
  return Object.fromEntries(fnNames.map((name) => [name, vi.fn()])) as Record<T, ReturnType<typeof vi.fn>>
}

/**
 * Create a vi.fn() wrapper around an API implementation.
 * NOTE: This does NOT install a module mock. You must wire the result into
 * vi.mock('@core/http/client', ...) yourself, or use vi.spyOn directly.
 *
 * Usage in a test file:
 *   vi.mock('@core/http/client', () => ({ apiRequest: createApiRequestMock(impl) }))
 */
export function createApiRequestMock(implementation: (path: string, options?: unknown) => Promise<unknown>) {
  return vi.fn(implementation)
}

/** @deprecated Use createApiRequestMock instead */
export const mockApiRequest = createApiRequestMock
