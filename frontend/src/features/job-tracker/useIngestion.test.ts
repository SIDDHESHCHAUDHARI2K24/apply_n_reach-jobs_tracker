import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as jtApiModule from '@features/job-tracker/jobTrackerApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/job-tracker/jobTrackerApi', () => ({
  jobTrackerApi: {
    refreshExtraction: vi.fn(),
    getLatestExtracted: vi.fn(),
    getExtractionRuns: vi.fn(),
  },
}))

const mockApi = jtApiModule.jobTrackerApi as unknown as {
  refreshExtraction: ReturnType<typeof vi.fn>
  getLatestExtracted: ReturnType<typeof vi.fn>
  getExtractionRuns: ReturnType<typeof vi.fn>
}

beforeEach(() => vi.clearAllMocks())

describe('useIngestion', () => {
  it('starts extraction and loads details on success', async () => {
    mockApi.refreshExtraction.mockResolvedValueOnce({ run_id: 'r1' })
    mockApi.getLatestExtracted.mockResolvedValueOnce({ id: 'e1', run_id: 'r1', company: 'ACME', role: 'SWE', raw_text: null, created_at: '' })
    mockApi.getExtractionRuns.mockResolvedValueOnce([])
    const { useIngestion } = await import('./ingestion/useIngestion')
    const { result } = renderHook(() => useIngestion())
    await act(async () => { await result.current.refresh() })
    expect(result.current.lastRunId).toBe('r1')
    expect(result.current.latestDetails?.company).toBe('ACME')
    expect(result.current.isRefreshing).toBe(false)
  })

  it('handles 409 (extraction in-flight)', async () => {
    mockApi.refreshExtraction.mockRejectedValueOnce(new HttpError('In flight', 409, 409))
    const { useIngestion } = await import('./ingestion/useIngestion')
    const { result } = renderHook(() => useIngestion())
    await act(async () => { await result.current.refresh() })
    expect(result.current.isInFlight).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('sets error on non-409 failure', async () => {
    mockApi.refreshExtraction.mockRejectedValueOnce(new HttpError('Server error', 500))
    const { useIngestion } = await import('./ingestion/useIngestion')
    const { result } = renderHook(() => useIngestion())
    await act(async () => { await result.current.refresh() })
    expect(result.current.error).toBe('Server error')
    expect(result.current.isInFlight).toBe(false)
  })

  it('loadRuns fetches details and runs', async () => {
    mockApi.getLatestExtracted.mockResolvedValueOnce(null)
    mockApi.getExtractionRuns.mockResolvedValueOnce([{ id: 'r1', user_id: 'u1', url: 'https://example.com', status: 'completed', error_message: null, created_at: '' }])
    const { useIngestion } = await import('./ingestion/useIngestion')
    const { result } = renderHook(() => useIngestion())
    await act(async () => { await result.current.loadRuns() })
    expect(result.current.runs).toHaveLength(1)
  })
})
