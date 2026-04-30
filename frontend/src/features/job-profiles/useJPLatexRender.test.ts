import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as jpApiModule from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/job-profiles/jobProfileApi', () => ({
  jobProfileApi: {
    triggerRender: vi.fn(),
    getResumeMetadata: vi.fn(),
    downloadPdf: vi.fn(),
  },
}))

const mockApi = jpApiModule.jobProfileApi as unknown as {
  triggerRender: ReturnType<typeof vi.fn>
  getResumeMetadata: ReturnType<typeof vi.fn>
  downloadPdf: ReturnType<typeof vi.fn>
}

const completedMeta = {
  job_profile_id: 'jp1',
  status: 'completed' as const,
  template_name: 'jakes_resume_v1',
  rendered_at: '2026-01-01T00:00:00Z',
  layout_json: {},
  error_message: null,
  created_at: null,
  updated_at: null,
}

beforeEach(() => vi.clearAllMocks())
afterEach(() => {
  vi.clearAllTimers()
})

describe('useJPLatexRender', () => {
  it('loads existing metadata on mount', async () => {
    mockApi.getResumeMetadata.mockResolvedValueOnce(completedMeta)

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => {})
    expect(result.current.metadata?.status).toBe('completed')
    expect(mockApi.getResumeMetadata).toHaveBeenCalledWith('jp1')
  })

  it('ignores 404 metadata on mount', async () => {
    mockApi.getResumeMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => {})

    expect(result.current.metadata).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('triggers render once and updates completed metadata', async () => {
    mockApi.getResumeMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    mockApi.triggerRender.mockResolvedValueOnce(completedMeta)

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })
    expect(result.current.isRendering).toBe(false)
    expect(result.current.metadata?.status).toBe('completed')
    expect(mockApi.triggerRender).toHaveBeenCalledTimes(1)
  })

  it('blocks duplicate trigger calls while rendering', async () => {
    mockApi.getResumeMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    let resolveRender: ((value: typeof completedMeta) => void) | null = null
    mockApi.triggerRender.mockImplementation(
      () => new Promise<typeof completedMeta>((resolve) => { resolveRender = resolve }),
    )

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => {
      const first = result.current.triggerRender()
      const second = result.current.triggerRender()
      await Promise.resolve()
      expect(mockApi.triggerRender).toHaveBeenCalledTimes(1)
      resolveRender?.(completedMeta)
      await Promise.all([first, second])
    })
  })

  it('sets error on render trigger failure', async () => {
    mockApi.getResumeMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    mockApi.triggerRender.mockRejectedValueOnce(new HttpError('Server error', 500))

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })

    expect(result.current.error).toBe('Server error')
    expect(result.current.isRendering).toBe(false)
    expect(result.current.timedOut).toBe(false)
  })

  it('downloadPdf creates a blob URL and triggers download', async () => {
    const mockBlob = new Blob(['%PDF'], { type: 'application/pdf' })
    mockApi.downloadPdf.mockResolvedValueOnce(mockBlob)

    const mockUrl = 'blob:http://localhost/fake-url'
    const createObjectURLMock = vi.fn(() => mockUrl)
    const revokeObjectURLMock = vi.fn()
    globalThis.URL.createObjectURL = createObjectURLMock
    globalThis.URL.revokeObjectURL = revokeObjectURLMock

    const mockAnchor = { href: '', download: '', click: vi.fn() }
    const originalCreateElement = document.createElement.bind(document)
    vi.spyOn(document, 'createElement').mockImplementation((tag: string, ...args: unknown[]) => {
      if (tag === 'a') return mockAnchor as unknown as HTMLElement
      return originalCreateElement(tag, ...(args as [ElementCreationOptions?]))
    })

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.downloadPdf() })

    expect(mockApi.downloadPdf).toHaveBeenCalledWith('jp1')
    expect(createObjectURLMock).toHaveBeenCalledWith(mockBlob)
    expect(mockAnchor.click).toHaveBeenCalled()
    expect(mockAnchor.download).toBe('resume-jp1.pdf')
  })
})
