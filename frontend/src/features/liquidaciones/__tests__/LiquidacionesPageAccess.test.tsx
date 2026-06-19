import { screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import LiquidacionesPage from '../pages/LiquidacionesPage'

const mockUseAuth = vi.fn()
vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock('../hooks/useLiquidacionesApi', () => ({
  useLiquidaciones: () => ({ data: undefined, isLoading: false, isError: false }),
  useExportarPlanilla: () => ({ mutate: vi.fn(), isPending: false }),
  useCalcularLiquidacion: () => ({ mutate: vi.fn(), isPending: false }),
}))

vi.mock('../components/FiltrosPeriodo', () => ({ default: () => <div>FiltrosPeriodo</div> }))
vi.mock('../components/KpisCabecera', () => ({ default: () => <div>KpisCabecera</div> }))
vi.mock('../components/GrillaSegmentada', () => ({ default: () => <div>GrillaSegmentada</div> }))
vi.mock('../components/DetalleLiquidacion', () => ({ default: () => null }))
vi.mock('../components/CierreConfirmacion', () => ({ default: () => null }))
vi.mock('../components/HistorialLiquidaciones', () => ({ default: () => <div>HistorialLiquidaciones</div> }))

describe('LiquidacionesPage — acceso con permiso wildcard de modulo (liquidaciones:*)', () => {
  it('FINANZAS con liquidaciones:* (sin *:* global) accede, no ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'finanzas-1', permissions: ['liquidaciones:*', 'facturas:*'] },
      logout: vi.fn(),
    })

    renderWithProviders(<LiquidacionesPage />)

    expect(screen.queryByText(/Acceso denegado/)).not.toBeInTheDocument()
    expect(screen.getByText('Liquidaciones')).toBeInTheDocument()
  })

  it('un rol sin permiso de liquidaciones ve "Acceso denegado"', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'alumno-1', permissions: ['coloquios:reservar'] },
      logout: vi.fn(),
    })

    renderWithProviders(<LiquidacionesPage />)

    expect(screen.getByText(/Acceso denegado/)).toBeInTheDocument()
  })
})
