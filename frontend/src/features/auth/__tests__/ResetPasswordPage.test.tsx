import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ResetPasswordPage from '../pages/ResetPasswordPage'

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
    <MemoryRouter initialEntries={['/reset-password?token=reset-token']}>
      <ResetPasswordPage />
    </MemoryRouter>,
  )
}

describe('ResetPasswordPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('validates password match', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Nueva contraseña'), 'password123')
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'different456')
    await user.click(screen.getByRole('button', { name: 'Restablecer contraseña' }))

    expect(
      await screen.findByText(/Las contraseñas no coinciden/),
    ).toBeInTheDocument()
    expect(mockPost).not.toHaveBeenCalled()
  })
})
