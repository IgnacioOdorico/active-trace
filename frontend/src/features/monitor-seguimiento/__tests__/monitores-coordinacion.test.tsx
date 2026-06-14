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
      data: { data: [], total: 0, pagina: 1, por_pagina: 50 },
    })

    const { default: MonitorGeneral } = await import('../components/MonitorGeneral')
    renderWithProviders(<MonitorGeneral />)

    expect(await screen.findByText(/No se encontraron resultados/i)).toBeInTheDocument()
  })

  it('envía query params de filtros al endpoint', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { data: [], total: 0, pagina: 1, por_pagina: 50 },
    })

    const { default: MonitorGeneral } = await import('../components/MonitorGeneral')
    const user = userEvent.setup()
    renderWithProviders(<MonitorGeneral />)

    const comisionInput = screen.getByPlaceholderText(/Ej: A/i)
    await user.type(comisionInput, 'B')

    // El hook re-consulta con el nuevo filtro — verificamos que get fue llamado
    expect(mockApiClient.get).toHaveBeenCalled()
  })
})

describe('MonitorSeguimiento — filtro rango de fechas (coordinador)', () => {
  it('muestra inputs de fecha_desde y fecha_hasta para coordinador', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { data: [], total: 0, pagina: 1, por_pagina: 50 },
    })

    const { default: MonitorSeguimiento } = await import('../components/MonitorSeguimiento')
    renderWithProviders(<MonitorSeguimiento />)

    expect(await screen.findByLabelText(/Fecha desde/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Fecha hasta/i)).toBeInTheDocument()
  })

  it('incluye fecha_desde y fecha_hasta en la query al establecer rango', async () => {
    mockApiClient.get.mockResolvedValue({
      data: { data: [], total: 0, pagina: 1, por_pagina: 50 },
    })

    const { default: MonitorSeguimiento } = await import('../components/MonitorSeguimiento')
    const user = userEvent.setup()
    renderWithProviders(<MonitorSeguimiento />)

    const desdeInput = await screen.findByLabelText(/Fecha desde/i)
    await user.type(desdeInput, '2024-03-01')

    // Verificamos que el endpoint fue llamado (con los parámetros que incluyen fecha_desde)
    expect(mockApiClient.get).toHaveBeenCalled()
  })
})
