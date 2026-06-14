import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import MetricasColoquios from '../components/MetricasColoquios'
import ConvocatoriaForm from '../components/ConvocatoriaForm'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('MetricasColoquios — render', () => {
  it('muestra las cuatro métricas obtenidas del endpoint', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        total_alumnos: 120,
        instancias_activas: 3,
        reservas_activas: 45,
        notas_registradas: 30,
      },
    })

    renderWithProviders(<MetricasColoquios />)

    expect(await screen.findByText('120')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('45')).toBeInTheDocument()
    expect(screen.getByText('30')).toBeInTheDocument()
    expect(screen.getByText(/Alumnos cargados/i)).toBeInTheDocument()
    expect(screen.getByText(/Instancias activas/i)).toBeInTheDocument()
    expect(screen.getByText(/Reservas activas/i)).toBeInTheDocument()
    expect(screen.getByText(/Notas registradas/i)).toBeInTheDocument()
  })

  it('muestra error cuando el endpoint falla', async () => {
    mockApiClient.get.mockRejectedValueOnce(new Error('Network error'))
    renderWithProviders(<MetricasColoquios />)
    expect(await screen.findByText(/Error al cargar métricas/i)).toBeInTheDocument()
  })
})

describe('ConvocatoriaForm — crear convocatoria', () => {
  it('bloquea envío con dias_disponibles vacío', async () => {
    const user = userEvent.setup()
    renderWithProviders(<ConvocatoriaForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    await user.type(screen.getByPlaceholderText(/ID de la materia/i), 'mat-1')
    await user.type(screen.getByPlaceholderText(/Primer llamado/i), 'Primer llamado')
    // No se selecciona ningún día

    await user.click(screen.getByRole('button', { name: /Crear convocatoria/i }))

    expect(await screen.findByText(/al menos un día/i)).toBeInTheDocument()
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })

  it('llama POST /api/coloquios con los datos correctos', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: { id: 'col-1' } })

    const user = userEvent.setup()
    renderWithProviders(<ConvocatoriaForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    await user.type(screen.getByPlaceholderText(/ID de la materia/i), 'mat-1')
    await user.type(screen.getByPlaceholderText(/Primer llamado/i), 'Primer llamado')
    await user.click(screen.getByRole('button', { name: /Lunes/i }))
    await user.clear(screen.getByRole('spinbutton'))
    await user.type(screen.getByRole('spinbutton'), '10')

    await user.click(screen.getByRole('button', { name: /Crear convocatoria/i }))

    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/api/coloquios',
      expect.objectContaining({
        materia_id: 'mat-1',
        instancia: 'Primer llamado',
        dias_disponibles: ['Lunes'],
        cupo_por_dia: 10,
      }),
    )
  })
})
