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

vi.useFakeTimers()

const mockApi = jpApiModule.jobProfileApi as unknown as {
  triggerRender: ReturnType<typeof vi.fn>
  getResumeMetadata: ReturnType<typeof vi.fn>
  downloadPdf: ReturnType<typeof vi.fn>
}

const pendingMeta = { job_profile_id: 'jp1', status: 'pending' as const, latex_source: null, pdf_url: null, error_message: null, created_at: '', updated_at: '' }
const completedMeta = { ...pendingMeta, status: 'completed' as const }
const failedMeta = { ...pendingMeta, status: 'failed' as const, error_message: 'LaTeX error' }

beforeEach(() => vi.clearAllMocks())
afterEach(() => vi.useRealTimers())

describe('useJPLatexRender', () => {
  beforeEach(() => vi.useFakeTimers())

  it('triggers render and polls until completed', async () => {
    mockApi.triggerRender.mockResolvedValueOnce(pendingMeta)
    mockApi.getResumeMetadata
      .mockResolvedValueOnce(pendingMeta)
      .mockResolvedValueOnce(completedMeta)

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })
    expect(result.current.isRendering).toBe(true)
    expect(result.current.metadata?.status).toBe('pending')

    // Advance timer to trigger first poll
    await act(async () => { vi.advanceTimersByTime(3000) })
    await act(async () => {})

    // Advance again for second poll -> completed
    await act(async () => { vi.advanceTimersByTime(3000) })
    await act(async () => {})

    expect(result.current.isRendering).toBe(false)
    expect(result.current.metadata?.status).toBe('completed')
  })

  it('stops polling on failed status', async () => {
    mockApi.triggerRender.mockResolvedValueOnce(pendingMeta)
    mockApi.getResumeMetadata.mockResolvedValueOnce(failedMeta)

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })
    await act(async () => { vi.advanceTimersByTime(3000) })
    await act(async () => {})

    expect(result.current.isRendering).toBe(false)
    expect(result.current.metadata?.status).toBe('failed')
  })

  it('times out after MAX_RETRIES polls', async () => {
    mockApi.triggerRender.mockResolvedValueOnce(pendingMeta)
    mockApi.getResumeMetadata.mockResolvedValue(pendingMeta)

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })

    // Advance past MAX_RETRIES (20 * 3000ms = 60000ms)
    for (let i = 0; i < 21; i++) {
      await act(async () => { vi.advanceTimersByTime(3000) })
      await act(async () => {})
    }

    expect(result.current.timedOut).toBe(true)
    expect(result.current.isRendering).toBe(false)
  })

  it('sets error on render trigger failure', async () => {
    mockApi.triggerRender.mockRejectedValueOnce(new HttpError('Server error', 500))

    const { useJPLatexRender } = await import('./render/useJPLatexRender')
    const { result } = renderHook(() => useJPLatexRender('jp1'))

    await act(async () => { await result.current.triggerRender() })

    expect(result.current.error).toBe('Server error')
    expect(result.current.isRendering).toBe(false)
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
