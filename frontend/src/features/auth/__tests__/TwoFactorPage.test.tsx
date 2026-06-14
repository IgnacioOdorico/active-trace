import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import TwoFactorPage from '../pages/TwoFactorPage'

const mockVerify2fa = vi.fn()

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    verify2fa: mockVerify2fa,
  }),
}))

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/login/2fa?token=test-token']}>
      <TwoFactorPage />
    </MemoryRouter>,
  )
}

describe('TwoFactorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('validates 6-digit code', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText('Código de verificación'), '123')
    await user.click(screen.getByRole('button', { name: 'Verificar' }))

    expect(
      await screen.findByText(/debe tener exactamente 6 dígitos/),
    ).toBeInTheDocument()
    expect(mockVerify2fa).not.toHaveBeenCalled()
  })
})
