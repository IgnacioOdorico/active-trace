import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import LoginPage from '../pages/LoginPage'

const mockLogin = vi.fn()
const mockNavigate = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: false,
    requires2fa: false,
    login: mockLogin,
    logout: vi.fn(),
    getAccessToken: vi.fn(() => null),
    verify2fa: vi.fn(),
  }),
}))

function renderPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders email, password fields and submit button', () => {
    renderPage()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ingresar' })).toBeInTheDocument()
  })

  it('validates empty fields and invalid email (no API call)', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(await screen.findByText(/Ingrese un email válido/)).toBeInTheDocument()
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('calls POST /api/auth/login on valid submit (mocked)', async () => {
    mockLogin.mockResolvedValueOnce({ access_token: 'a', refresh_token: 'b' })
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('shows backend error message', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Credenciales inválidas'))
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(await screen.findByText('Credenciales inválidas')).toBeInTheDocument()
  })

  it('redirects on successful login', async () => {
    mockLogin.mockResolvedValueOnce({ access_token: 'a', refresh_token: 'b' })
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    await vi.waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true })
    })
  })

  it('shows loading state during submission', async () => {
    let resolveLogin: (v: unknown) => void = () => {}
    mockLogin.mockImplementation(
      () => new Promise((resolve) => { resolveLogin = resolve }),
    )
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'password123')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(screen.getByRole('button', { name: /Ingresando/ })).toBeDisabled()
    resolveLogin({ access_token: 'a', refresh_token: 'b' })
  })
})
