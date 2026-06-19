import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import GrillaSegmentada from '../components/GrillaSegmentada'
import KpisCabecera from '../components/KpisCabecera'
import CierreConfirmacion from '../components/CierreConfirmacion'
import DetalleLiquidacion from '../components/DetalleLiquidacion'
import HistorialLiquidaciones from '../components/HistorialLiquidaciones'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../../estructura-academica/hooks/useEstructuraApi', () => ({
  useCohortes: vi.fn().mockReturnValue({ data: [] }),
}))

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { roles: ['FINANZAS'], permissions: ['*:*'] },
    isAuthenticated: true,
    isLoading: false,
    logout: vi.fn(),
    getAccessToken: vi.fn(() => 'token'),
    accessToken: 'token',
  }),
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
  window.URL.createObjectURL = vi.fn(() => 'blob:fake-url')
  window.URL.revokeObjectURL = vi.fn()
})

const liqGeneral = {
  id: 'liq-1',
  usuario_id: 'u-1',
  docente_nombre: 'Ana García',
  rol: 'PROFESOR',
  comisiones: ['A', 'B', 'C'],
  monto_base: 50000,
  monto_plus: 0,
  total: 50000,
  es_nexo: false,
  excluido_por_factura: false,
  estado: 'Abierta' as const,
  periodo: '2024-06',
  cohorte_id: 'c-1',
}

const liqNexo = {
  ...liqGeneral,
  id: 'liq-2',
  docente_nombre: 'Carlos López',
  es_nexo: true,
  excluido_por_factura: false,
}

const liqFacturante = {
  ...liqGeneral,
  id: 'liq-3',
  docente_nombre: 'María Torres',
  es_nexo: false,
  excluido_por_factura: true,
}

// 9.1 — Grilla segmentada: renderiza tres segmentos
describe('GrillaSegmentada — tres segmentos', () => {
  it('renderiza segmento General, NEXO y Facturantes correctamente', () => {
    renderWithProviders(
      <GrillaSegmentada
        items={[liqGeneral, liqNexo, liqFacturante]}
        onVerDetalle={vi.fn()}
      />,
    )
    expect(screen.getByText(/General/i)).toBeInTheDocument()
    expect(screen.getByText(/NEXO/i)).toBeInTheDocument()
    expect(screen.getByText(/Facturantes/i)).toBeInTheDocument()
    expect(screen.getByText('Ana García')).toBeInTheDocument()
    expect(screen.getByText('Carlos López')).toBeInTheDocument()
    expect(screen.getByText('María Torres')).toBeInTheDocument()
  })

  it('muestra estado vacío cuando no hay items', () => {
    renderWithProviders(
      <GrillaSegmentada items={[]} onVerDetalle={vi.fn()} />,
    )
    expect(screen.getByText(/sin liquidaciones/i)).toBeInTheDocument()
  })

  it('marca Facturantes como informativo', () => {
    renderWithProviders(
      <GrillaSegmentada items={[liqFacturante]} onVerDetalle={vi.fn()} />,
    )
    expect(screen.getByText(/Informativo/i)).toBeInTheDocument()
  })
})

// 9.1 — KPIs del endpoint (no recalcula en cliente)
describe('KpisCabecera — muestra datos del endpoint', () => {
  it('llama /api/liquidaciones/kpis y renderiza los totales', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        total_general: 100000,
        total_nexo: 50000,
        total_facturas_pendientes: 30000,
        total_facturas_abonadas: 10000,
        cantidad_docentes_general: 5,
        cantidad_docentes_nexo: 2,
        cantidad_docentes_facturantes: 1,
      },
    })

    renderWithProviders(<KpisCabecera periodo="2024-06" />)

    expect(await screen.findByText(/Docentes generales/i)).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('no renderiza nada si no hay período', () => {
    const { container } = renderWithProviders(<KpisCabecera periodo={undefined} />)
    expect(container.firstChild).toBeNull()
  })
})

describe('DetalleLiquidacion — sin plus_detalle inventado (regresión crash)', () => {
  it('renderiza el detalle usando monto_plus/total reales sin crashear', () => {
    renderWithProviders(
      <DetalleLiquidacion liquidacion={liqGeneral} onClose={vi.fn()} />,
    )
    expect(screen.getByText('Ana García')).toBeInTheDocument()
    expect(screen.getByText('A, B, C')).toBeInTheDocument()
  })

  it('muestra el plus salarial cuando monto_plus > 0', () => {
    renderWithProviders(
      <DetalleLiquidacion
        liquidacion={{ ...liqGeneral, monto_plus: 5000, total: 55000 }}
        onClose={vi.fn()}
      />,
    )
    expect(screen.getByText(/Plus salarial/i)).toBeInTheDocument()
  })
})

// 9.2 — Cierre: confirmación obligatoria, POST al confirmar, manejo 409
describe('CierreConfirmacion — flujo de cierre', () => {
  it('muestra aviso de irreversibilidad antes de confirmar', () => {
    renderWithProviders(
      <CierreConfirmacion
        liquidacion={liqGeneral}
        onClosed={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    expect(screen.getByText(/irreversible/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Confirmar cierre/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Cancelar/i })).toBeInTheDocument()
  })

  it('llama POST al confirmar y dispara onClosed', async () => {
    const onClosed = vi.fn()
    mockApiClient.post.mockResolvedValueOnce({ data: { estado: 'Cerrada' } })

    renderWithProviders(
      <CierreConfirmacion
        liquidacion={liqGeneral}
        onClosed={onClosed}
        onCancel={vi.fn()}
      />,
    )

    await userEvent.setup().click(screen.getByRole('button', { name: /Confirmar cierre/i }))
    await waitFor(() => expect(mockApiClient.post).toHaveBeenCalledWith('/api/liquidaciones/liq-1/cerrar'))
    await waitFor(() => expect(onClosed).toHaveBeenCalled())
  })

  it('maneja 409 (ya cerrada) mostrando mensaje no destructivo', async () => {
    const onClosed = vi.fn()
    mockApiClient.post.mockRejectedValueOnce({
      response: { status: 409, data: { detail: 'LIQUIDACION_YA_CERRADA' } },
    })

    renderWithProviders(
      <CierreConfirmacion
        liquidacion={liqGeneral}
        onClosed={onClosed}
        onCancel={vi.fn()}
      />,
    )

    await userEvent.setup().click(screen.getByRole('button', { name: /Confirmar cierre/i }))
    await waitFor(() => expect(screen.getByText(/ya estaba cerrada/i)).toBeInTheDocument())
    // onClosed se llama igual (idempotente)
    await waitFor(() => expect(onClosed).toHaveBeenCalled())
  })
})

describe('HistorialLiquidaciones — filas agregadas por período (no por docente)', () => {
  it('renderiza total_docentes y monto_total del agregado real del backend', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'c-1:2026-05',
            periodo: '2026-05',
            cohorte_id: 'c-1',
            estado: 'Cerrada',
            total_docentes: 3,
            monto_total: 150000,
          },
        ],
        total: 1,
      },
    })

    renderWithProviders(<HistorialLiquidaciones />)

    expect(await screen.findByText('2026-05')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })
})

// Exportar planilla: botón deshabilitado sin período, GET con responseType blob al hacer click
describe('LiquidacionesPage — Exportar planilla', () => {
  it('el botón está deshabilitado mientras no haya un período seleccionado', async () => {
    const { default: LiquidacionesPage } = await import('../pages/LiquidacionesPage')
    renderWithProviders(<LiquidacionesPage />)

    const boton = screen.getByRole('button', { name: /Exportar planilla/i })
    expect(boton).toBeDisabled()
  })

  it('al seleccionar período se habilita y dispara GET /api/liquidaciones/exportar con responseType blob', async () => {
    mockApiClient.get.mockImplementation((url: string) => {
      if (url.includes('/api/liquidaciones/exportar')) {
        return Promise.resolve({ data: new Blob(['fake-xlsx']) })
      }
      if (url.includes('/api/liquidaciones/kpis')) {
        return Promise.resolve({
          data: {
            total_general: 0, total_nexo: 0, total_facturas_pendientes: 0,
            total_facturas_abonadas: 0, cantidad_docentes_general: 0, cantidad_docentes_nexo: 0,
            cantidad_docentes_facturantes: 0,
          },
        })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })

    const { default: LiquidacionesPage } = await import('../pages/LiquidacionesPage')
    const user = userEvent.setup()
    renderWithProviders(<LiquidacionesPage />)

    const periodoInput = screen.getByLabelText(/Período/i)
    await user.type(periodoInput, '2026-06')

    const boton = await screen.findByRole('button', { name: /Exportar planilla/i })
    expect(boton).not.toBeDisabled()

    await user.click(boton)

    await waitFor(() => {
      const exportCall = mockApiClient.get.mock.calls.find(([url]) =>
        (url as string).includes('/api/liquidaciones/exportar'),
      )
      expect(exportCall).toBeDefined()
      expect((exportCall as unknown[])[0] as string).toContain('periodo=2026-06')
      expect((exportCall as unknown[])[1]).toMatchObject({ responseType: 'blob' })
    })
  })
})

describe('LiquidacionesPage — Calcular liquidación', () => {
  beforeEach(() => {
    mockApiClient.get.mockImplementation((url: string) => {
      if (url.includes('/api/liquidaciones/kpis')) {
        return Promise.resolve({
          data: {
            total_general: 0, total_nexo: 0, total_facturas_pendientes: 0,
            total_facturas_abonadas: 0, cantidad_docentes_general: 0, cantidad_docentes_nexo: 0,
            cantidad_docentes_facturantes: 0,
          },
        })
      }
      return Promise.resolve({ data: { items: [], total: 0 } })
    })
  })

  it('el botón está deshabilitado sin cohorte y período seleccionados', async () => {
    const { default: LiquidacionesPage } = await import('../pages/LiquidacionesPage')
    renderWithProviders(<LiquidacionesPage />)

    const boton = screen.getByRole('button', { name: /Calcular liquidación/i })
    expect(boton).toBeDisabled()
  })

  it('al seleccionar cohorte y período se habilita y dispara POST /api/liquidaciones/calcular', async () => {
    const { useCohortes } = await import('../../estructura-academica/hooks/useEstructuraApi')
    vi.mocked(useCohortes).mockReturnValue({
      data: [{ id: 'c-1', nombre: 'Cohorte 2026' }],
    } as ReturnType<typeof useCohortes>)
    mockApiClient.post.mockResolvedValueOnce({ data: { liquidaciones: [], total: 3 } })

    const { default: LiquidacionesPage } = await import('../pages/LiquidacionesPage')
    const user = userEvent.setup()
    renderWithProviders(<LiquidacionesPage />)

    await user.selectOptions(screen.getByLabelText(/Cohorte/i), 'c-1')
    await user.type(screen.getByLabelText(/Período/i), '2026-06')

    const boton = await screen.findByRole('button', { name: /Calcular liquidación/i })
    expect(boton).not.toBeDisabled()

    await user.click(boton)

    await waitFor(() => {
      expect(mockApiClient.post).toHaveBeenCalledWith('/api/liquidaciones/calcular', {
        cohorte_id: 'c-1',
        periodo: '2026-06',
      })
    })
    expect(await screen.findByText(/Se calcularon 3 liquidaciones/i)).toBeInTheDocument()
  })

  it('maneja 409 (período cerrado) mostrando mensaje no destructivo', async () => {
    const { useCohortes } = await import('../../estructura-academica/hooks/useEstructuraApi')
    vi.mocked(useCohortes).mockReturnValue({
      data: [{ id: 'c-1', nombre: 'Cohorte 2026' }],
    } as ReturnType<typeof useCohortes>)
    mockApiClient.post.mockRejectedValueOnce({
      response: { status: 409, data: { detail: 'El período ya está cerrado' } },
    })

    const { default: LiquidacionesPage } = await import('../pages/LiquidacionesPage')
    const user = userEvent.setup()
    renderWithProviders(<LiquidacionesPage />)

    await user.selectOptions(screen.getByLabelText(/Cohorte/i), 'c-1')
    await user.type(screen.getByLabelText(/Período/i), '2026-06')

    const boton = await screen.findByRole('button', { name: /Calcular liquidación/i })
    await user.click(boton)

    expect(await screen.findByText(/ya está cerrado/i)).toBeInTheDocument()
  })
})
