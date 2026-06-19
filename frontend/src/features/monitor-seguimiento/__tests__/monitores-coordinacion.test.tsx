import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('../../academico/hooks/useMaterias', () => ({
  useMaterias: () => ({ data: [], isLoading: false }),
}))

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { roles: ['coordinador'], permissions: ['monitores:ver', '*:*'] },
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
})

describe('MonitorGeneral — filtros y Limpiar', () => {
  it('renderiza los filtros y el listado vacío', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, pagina: 1, por_pagina: 50, total_paginas: 0 },
    })

    const { default: MonitorGeneral } = await import('../components/MonitorGeneral')
    renderWithProviders(<MonitorGeneral />)

    expect(await screen.findByText(/No se encontraron resultados/i)).toBeInTheDocument()
  })

  it('envía query params de filtros al endpoint', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, pagina: 1, por_pagina: 50, total_paginas: 0 },
    })

    const { default: MonitorGeneral } = await import('../components/MonitorGeneral')
    const user = userEvent.setup()
    renderWithProviders(<MonitorGeneral />)

    const comisionInput = screen.getByPlaceholderText(/Ej: A/i)
    await user.type(comisionInput, 'B')

    expect(mockApiClient.get).toHaveBeenCalled()
    const calls = mockApiClient.get.mock.calls
    const lastCall = calls[calls.length - 1]![0] as string
    expect(lastCall).toContain('comision=B')
  })
})

describe('MonitorSeguimiento — filtro rango de fechas (coordinador)', () => {
  it('muestra inputs de fecha desde/hasta para coordinador', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, pagina: 1, por_pagina: 50, total_paginas: 0 },
    })

    const { default: MonitorSeguimiento } = await import('../components/MonitorSeguimiento')
    renderWithProviders(<MonitorSeguimiento />)

    expect(await screen.findByLabelText(/Fecha desde/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Fecha hasta/i)).toBeInTheDocument()
  })

  it('envía "desde" y "hasta" (no fecha_desde/fecha_hasta) al establecer el rango', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, pagina: 1, por_pagina: 50, total_paginas: 0 },
    })

    const { default: MonitorSeguimiento } = await import('../components/MonitorSeguimiento')
    const user = userEvent.setup()
    renderWithProviders(<MonitorSeguimiento />)

    const desdeInput = await screen.findByLabelText(/Fecha desde/i)
    await user.type(desdeInput, '2024-03-01')
    const hastaInput = screen.getByLabelText(/Fecha hasta/i)
    await user.type(hastaInput, '2024-03-31')

    const calls = mockApiClient.get.mock.calls
    const lastCall = calls[calls.length - 1]![0] as string
    expect(lastCall).toContain('desde=2024-03-01')
    expect(lastCall).toContain('hasta=2024-03-31')
    expect(lastCall).not.toContain('fecha_desde')
    expect(lastCall).not.toContain('fecha_hasta')
  })

  it('muestra un filtro de Comisión (no de búsqueda de alumno, que el backend no soporta)', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { items: [], total: 0, pagina: 1, por_pagina: 50, total_paginas: 0 },
    })

    const { default: MonitorSeguimiento } = await import('../components/MonitorSeguimiento')
    const user = userEvent.setup()
    renderWithProviders(<MonitorSeguimiento />)

    const comisionInput = await screen.findByLabelText(/Comisión/i)
    await user.type(comisionInput, 'A')

    const calls = mockApiClient.get.mock.calls
    const lastCall = calls[calls.length - 1]![0] as string
    expect(lastCall).toContain('comision=A')
  })
})
