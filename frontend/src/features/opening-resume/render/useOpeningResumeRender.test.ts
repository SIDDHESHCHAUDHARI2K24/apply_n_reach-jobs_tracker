import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as orApiModule from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/opening-resume/openingResumeApi', () => ({
  openingResumeApi: {
    getRenderMetadata: vi.fn(),
    triggerRender: vi.fn(),
    downloadPdf: vi.fn(),
  },
}))

const mockApi = orApiModule.openingResumeApi as unknown as {
  getRenderMetadata: ReturnType<typeof vi.fn>
  triggerRender: ReturnType<typeof vi.fn>
  downloadPdf: ReturnType<typeof vi.fn>
}

const metadata = {
  resume_id: '42',
  template_name: 'jakes_resume_v1',
  updated_at: '2025-01-01T00:00:00Z',
  latex_length: 5000,
  pdf_size_bytes: 45000,
}

beforeEach(() => vi.clearAllMocks())

describe('useOpeningResumeRender', () => {
  it('loads render metadata on mount', async () => {
    mockApi.getRenderMetadata.mockResolvedValueOnce(metadata)
    const { useOpeningResumeRender } = await import('./useOpeningResumeRender')
    const { result } = renderHook(() => useOpeningResumeRender('o1'))
    await act(async () => {})
    expect(result.current.metadata).toEqual(metadata)
    expect(result.current.error).toBeNull()
  })

  it('handles 404 as never-rendered gracefully', async () => {
    mockApi.getRenderMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    const { useOpeningResumeRender } = await import('./useOpeningResumeRender')
    const { result } = renderHook(() => useOpeningResumeRender('o1'))
    await act(async () => {})
    expect(result.current.metadata).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('triggers render and updates metadata', async () => {
    mockApi.getRenderMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    mockApi.triggerRender.mockResolvedValueOnce(metadata)
    const { useOpeningResumeRender } = await import('./useOpeningResumeRender')
    const { result } = renderHook(() => useOpeningResumeRender('o1'))
    await act(async () => {})
    expect(result.current.metadata).toBeNull()
    let returned: unknown
    await act(async () => { returned = await result.current.triggerRender() })
    expect(returned).toEqual(metadata)
    expect(result.current.metadata).toEqual(metadata)
    expect(result.current.isRendering).toBe(false)
    expect(mockApi.triggerRender).toHaveBeenCalledWith('o1')
  })

  it('records render failure and clears error on retry success', async () => {
    mockApi.getRenderMetadata.mockRejectedValueOnce(new HttpError('Not found', 404))
    mockApi.triggerRender
      .mockRejectedValueOnce(new HttpError('LaTeX compilation failed', 500))
      .mockResolvedValueOnce(metadata)
    const { useOpeningResumeRender } = await import('./useOpeningResumeRender')
    const { result } = renderHook(() => useOpeningResumeRender('o1'))
    await act(async () => {})

    let failedReturn: unknown
    await act(async () => { failedReturn = await result.current.triggerRender() })
    expect(failedReturn).toBeNull()
    expect(result.current.metadata).toBeNull()
    expect(result.current.error).toBe('LaTeX compilation failed')

    let okReturn: unknown
    await act(async () => { okReturn = await result.current.triggerRender() })
    expect(okReturn).toEqual(metadata)
    expect(result.current.metadata).toEqual(metadata)
    expect(result.current.error).toBeNull()
  })

  it('downloads PDF', async () => {
    const blob = new Blob(['pdf'], { type: 'application/pdf' })
    mockApi.getRenderMetadata.mockResolvedValueOnce(metadata)
    mockApi.downloadPdf.mockResolvedValueOnce(blob)
    const { useOpeningResumeRender } = await import('./useOpeningResumeRender')
    const { result } = renderHook(() => useOpeningResumeRender('o1'))
    await act(async () => {})
    await act(async () => { await result.current.downloadPdf() })
    expect(mockApi.downloadPdf).toHaveBeenCalledWith('o1')
  })
})
