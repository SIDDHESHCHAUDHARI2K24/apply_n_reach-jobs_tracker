import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockApiRequest = vi.fn()

vi.mock('@core/config/env', () => ({
  API_BASE_URL: 'http://localhost:8000',
}))

vi.mock('@core/http/client', () => ({
  apiRequest: mockApiRequest,
}))

describe('jobTrackerApi email-agent methods', () => {
  beforeEach(() => {
    mockApiRequest.mockReset()
  })

  it('maps startEmailAgentRun response IDs to strings', async () => {
    const { jobTrackerApi } = await import('./jobTrackerApi')
    mockApiRequest.mockResolvedValueOnce({
      run_id: 11,
      opening_id: 99,
      status: 'running',
      message: 'Email agent run started',
    })

    const response = await jobTrackerApi.startEmailAgentRun('99', { recipient_type: 'recruiter' })

    expect(mockApiRequest).toHaveBeenCalledWith('/job-openings/99/email-agent/run', {
      method: 'POST',
      body: { recipient_type: 'recruiter' },
    })
    expect(response).toEqual({
      run_id: '11',
      opening_id: '99',
      status: 'running',
      message: 'Email agent run started',
    })
  })

  it('maps getEmailAgentStatus response shape', async () => {
    const { jobTrackerApi } = await import('./jobTrackerApi')
    mockApiRequest.mockResolvedValueOnce({
      run_id: 7,
      opening_id: 2,
      agent_status: 'running',
      current_node: 'subject_generator',
      events: [{ node: 'subject_generator', status: 'running' }],
      error_message: null,
      started_at: '2026-05-04T21:00:00Z',
      completed_at: null,
    })

    const response = await jobTrackerApi.getEmailAgentStatus('2')

    expect(response.run_id).toBe('7')
    expect(response.opening_id).toBe('2')
    expect(response.events).toHaveLength(1)
  })

  it('maps run list IDs to strings', async () => {
    const { jobTrackerApi } = await import('./jobTrackerApi')
    mockApiRequest.mockResolvedValueOnce([
      {
        id: 3,
        opening_id: 2,
        status: 'failed',
        current_node: 'email_generator',
        error_message: 'Boom',
        started_at: '2026-05-04T21:00:00Z',
        completed_at: '2026-05-04T21:00:10Z',
        created_at: '2026-05-04T20:59:59Z',
      },
    ])

    const response = await jobTrackerApi.getEmailAgentRuns('2')

    expect(response[0]).toMatchObject({
      id: '3',
      opening_id: '2',
      status: 'failed',
    })
  })

  it('maps resume response run_id to string', async () => {
    const { jobTrackerApi } = await import('./jobTrackerApi')
    mockApiRequest.mockResolvedValueOnce({
      run_id: 12,
      status: 'running',
      message: 'Resumed',
    })

    const response = await jobTrackerApi.resumeEmailAgent('9', { user_edits: [] })

    expect(response).toEqual({
      run_id: '12',
      status: 'running',
      message: 'Resumed',
    })
  })

  it('returns encoded stream URL', async () => {
    const { jobTrackerApi } = await import('./jobTrackerApi')

    const url = jobTrackerApi.getEmailAgentStreamUrl('id with spaces')

    expect(url).toBe('http://localhost:8000/job-openings/id%20with%20spaces/email-agent/stream')
  })
})
