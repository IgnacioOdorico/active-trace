import { describe, it, expect, vi, beforeEach } from 'vitest'

const { requestHandlers, responseErrorHandlers, mockInstance, mockRefreshPost } =
  vi.hoisted(() => {
    const reqHandlers: Array<(config: unknown) => unknown> = []
    const resErrorHandlers: Array<
      (error: unknown) => Promise<unknown>
    > = []

    const mInstance = Object.assign(
      vi.fn().mockResolvedValue({ data: { message: 'Retry success' } }),
      {
        defaults: { baseURL: 'http://test.com/api' },
        interceptors: {
          request: {
            use: vi.fn((handler: (config: unknown) => unknown) => {
              reqHandlers.push(handler)
            }),
          },
          response: {
            use: vi.fn(
              (
                _success: unknown,
                errorHandler: (error: unknown) => Promise<unknown>,
              ) => {
                resErrorHandlers.push(errorHandler)
              },
            ),
          },
        },
        get: vi.fn(),
        post: vi.fn(),
      },
    )

    return {
      requestHandlers: reqHandlers,
      responseErrorHandlers: resErrorHandlers,
      mockInstance: mInstance,
      mockRefreshPost: vi.fn(),
    }
  })

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockInstance),
    post: mockRefreshPost,
  },
}))

const httpClientModule = await import('../httpClient')

describe('httpClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('transparent refresh on 401 (mock two calls, assert retry succeeds)', async () => {
    httpClientModule.setupAuthInterceptors({
      getAccessToken: vi.fn(() => 'old-token'),
      getRefreshToken: vi.fn(() => 'refresh-token'),
      onTokenRefreshed: vi.fn(),
      onAuthFailure: vi.fn(),
      isLoggingOut: vi.fn(() => false),
    })

    const requestInterceptor = requestHandlers[0]
    const responseErrorHandler = responseErrorHandlers[0]
    expect(requestInterceptor).toBeDefined()
    expect(responseErrorHandler).toBeDefined()

    const testConfig = { headers: {} }
    requestInterceptor!(testConfig)
    expect(
      (testConfig as { headers: Record<string, string> }).headers.Authorization,
    ).toBe('Bearer old-token')

    const originalRequest = {
      headers: { Authorization: 'Bearer old-token' },
      _retry: false,
    }

    mockRefreshPost.mockResolvedValueOnce({
      data: { access_token: 'new-token', refresh_token: 'new-refresh' },
    })

    mockInstance.post.mockResolvedValueOnce({
      data: { message: 'Retry success' },
    })

    const error = {
      response: { status: 401 },
      config: originalRequest,
    }

    const retryPromise = responseErrorHandler!(error)
    await expect(retryPromise).resolves.toEqual({
      data: { message: 'Retry success' },
    })

    expect(mockRefreshPost).toHaveBeenCalledWith(
      'http://test.com/api/api/auth/refresh',
      { refresh_token: 'refresh-token' },
    )
  })

  it('redirects on failed refresh', async () => {
    const authFailureFn = vi.fn()

    httpClientModule.setupAuthInterceptors({
      getAccessToken: vi.fn(() => 'old-token'),
      getRefreshToken: vi.fn(() => 'refresh-token'),
      onTokenRefreshed: vi.fn(),
      onAuthFailure: authFailureFn,
      isLoggingOut: vi.fn(() => false),
    })

    const responseErrorHandler = responseErrorHandlers[0]
    expect(responseErrorHandler).toBeDefined()

    const originalRequest = { headers: {} as Record<string, string>, _retry: false }
    mockRefreshPost.mockRejectedValueOnce(new Error('Refresh failed'))

    const error = {
      response: { status: 401 },
      config: originalRequest,
    }

    await expect(responseErrorHandler!(error)).rejects.toThrow()
    expect(authFailureFn).toHaveBeenCalled()
  })
})
