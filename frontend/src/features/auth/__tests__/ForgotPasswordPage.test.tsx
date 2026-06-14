import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ForgotPasswordPage from '../pages/ForgotPasswordPage'

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}))

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    post: mockPost,
  },
  setupAuthInterceptors: vi.fn(),
}))

function renderPage() {
  return render(
    <MemoryRouter>
      <ForgotPasswordPage />
    </MemoryRouter>,
  )
}

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows success message after submit', async () => {
    mockPost.mockResolvedValueOnce({ data: { message: 'ok' } })
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.click(screen.getByRole('button', { name: 'Enviar solicitud' }))

    expect(await screen.findByText(/Solicitud Enviada/)).toBeInTheDocument()
    expect(mockPost).toHaveBeenCalledWith('/api/auth/forgot', {
      email: 'test@example.com',
    })
  })
})
