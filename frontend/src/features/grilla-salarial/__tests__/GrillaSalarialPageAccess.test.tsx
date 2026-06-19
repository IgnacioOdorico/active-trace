import { screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import GrillaSalarialPage from '../pages/GrillaSalarialPage'

const mockUseAuth = vi.fn()
vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock('../components/SalarioBaseABM', () => ({ default: () => <div>SalarioBaseABM</div> }))
vi.mock('../components/SalarioPlusABM', () => ({ default: () => null }))

describe('GrillaSalarialPage — acceso con permiso wildcard de modulo (liquidaciones:*)', () => {
  it('FINANZAS con liquidaciones:* (sin *:* global) accede, no ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'finanzas-1', permissions: ['liquidaciones:*'] },
      logout: vi.fn(),
    })

    renderWithProviders(<GrillaSalarialPage />)

    expect(screen.queryByText(/Acceso denegado/)).not.toBeInTheDocument()
    expect(screen.getByText('SalarioBaseABM')).toBeInTheDocument()
  })

  it('un rol sin permiso de liquidaciones ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'alumno-1', permissions: ['coloquios:reservar'] },
      logout: vi.fn(),
    })

    renderWithProviders(<GrillaSalarialPage />)

    expect(screen.getByText(/Acceso denegado/)).toBeInTheDocument()
  })
})
