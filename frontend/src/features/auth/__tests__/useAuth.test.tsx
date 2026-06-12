import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAuth, AuthProvider } from '../hooks/useAuth'

const { mockAxiosPost, mockInstance } = vi.hoisted(() => {
  const mInstance = Object.assign(
    vi.fn().mockResolvedValue({ data: {} }),
    {
      defaults: { baseURL: 'http://test.com' },
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      get: vi.fn(),
      post: vi.fn(),
    },
  )

  return {
    mockAxiosPost: vi.fn(),
    mockInstance: mInstance,
  }
})

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockInstance),
    post: mockAxiosPost,
  },
}))

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

function TestConsumer() {
  const { user, isAuthenticated, isLoading, login, logout, requires2fa } =
    useAuth()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'authenticated' : 'unauthenticated'}
      </div>
      {user && <div data-testid="user-email">{user.email}</div>}
      <div data-testid="requires2fa">{requires2fa ? 'true' : 'false'}</div>
      <button onClick={() => login('test@test.com', 'password123')}>
        Login
      </button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  )
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/']}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Remove stored tokens between tests
    for (const key of ['accessToken', 'refreshToken']) {
      try { localStorage.removeItem(key) } catch { /* ignore */ }
    }
  })

  it('login/logout flow with mocked API', async () => {
    mockInstance.post.mockResolvedValueOnce({
      data: {
        access_token: 'test-access',
        refresh_token: 'test-refresh',
      },
    })
    mockInstance.get.mockResolvedValueOnce({
      data: {
        id: '1',
        email: 'test@test.com',
        nombre: 'Test User',
        roles: ['user'],
        permissions: ['read'],
        tenant_id: 't1',
      },
    })

    renderWithProviders(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    )

    const user = userEvent.setup()
    await user.click(screen.getByText('Login'))

    await vi.waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated')
    })
    expect(screen.getByTestId('user-email')).toHaveTextContent('test@test.com')

    mockInstance.post.mockResolvedValueOnce({ data: {} })
    await user.click(screen.getByText('Logout'))

    await vi.waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent(
        'unauthenticated',
      )
    })
  })
})
