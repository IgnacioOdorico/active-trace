import { screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import FacturasPage from '../pages/FacturasPage'

const mockUseAuth = vi.fn()
vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock('../components/FacturasListado', () => ({ default: () => <div>FacturasListado</div> }))
vi.mock('../components/CargarFacturaForm', () => ({ default: () => null }))

describe('FacturasPage — acceso con permiso wildcard de modulo (facturas:*)', () => {
  it('FINANZAS con facturas:* (sin *:* global) accede, no ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'finanzas-1', permissions: ['facturas:*', 'liquidaciones:*'] },
      logout: vi.fn(),
    })

    renderWithProviders(<FacturasPage />)

    expect(screen.queryByText(/Acceso denegado/)).not.toBeInTheDocument()
    expect(screen.getByText('FacturasListado')).toBeInTheDocument()
  })

  it('un rol sin permiso de facturas ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'alumno-1', permissions: ['coloquios:reservar'] },
      logout: vi.fn(),
    })

    renderWithProviders(<FacturasPage />)

    expect(screen.getByText(/Acceso denegado/)).toBeInTheDocument()
  })
})
