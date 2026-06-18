import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import MetricasColoquios from '../components/MetricasColoquios'
import ConvocatoriaForm from '../components/ConvocatoriaForm'
import EditarConvocatoriaForm from '../components/EditarConvocatoriaForm'
import ListadoConvocatorias from '../components/ListadoConvocatorias'
import type { Convocatoria } from '../types'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

const MATERIAS_FIXTURE = [{ id: 'mat-1', nombre: 'Programación I' }]
const COHORTES_FIXTURE = [{ id: 'coh-1', nombre: '2026', carrera_id: 'carr-1' }]

const CONVOCATORIA_FIXTURE: Convocatoria = {
  id: 'col-1',
  materia_id: 'mat-1',
  cohorte_id: 'coh-1',
  tipo: 'Coloquio',
  instancia: 'Primer llamado',
  dias_disponibles: 5,
  total_convocados: 20,
  total_reservas_activas: 10,
  total_cupos_libres: 40,
}

function mockGetByUrl(routes: Record<string, unknown>) {
  const sorted = Object.entries(routes).sort((a, b) => b[0].length - a[0].length)
  mockApiClient.get.mockImplementation((url: string) => {
    for (const [path, data] of sorted) {
      if (url.includes(path)) return Promise.resolve({ data })
    }
    return Promise.resolve({ data: undefined })
  })
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('MetricasColoquios — render', () => {
  it('muestra las cuatro métricas obtenidas del endpoint con los nombres reales del backend', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        total_alumnos_convocados: 120,
        total_instancias_activas: 3,
        total_reservas_activas: 45,
        total_notas_registradas: 30,
      },
    })

    renderWithProviders(<MetricasColoquios />)

    expect(await screen.findByText('120')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('45')).toBeInTheDocument()
    expect(screen.getByText('30')).toBeInTheDocument()
  })

  it('muestra error cuando el endpoint falla', async () => {
    mockApiClient.get.mockRejectedValueOnce(new Error('Network error'))
    renderWithProviders(<MetricasColoquios />)
    expect(await screen.findByText(/Error al cargar métricas/i)).toBeInTheDocument()
  })
})

describe('ListadoConvocatorias — contrato real del backend', () => {
  it('lee "items" (no "data") y resuelve materia/cohorte por nombre', async () => {
    mockGetByUrl({
      '/api/coloquios': {
        items: [CONVOCATORIA_FIXTURE],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
      '/api/v1/admin/cohortes': COHORTES_FIXTURE,
    })

    renderWithProviders(<ListadoConvocatorias onEditar={vi.fn()} onImportar={vi.fn()} />)

    expect(await screen.findByText('Programación I')).toBeInTheDocument()
    expect(screen.getByText('2026')).toBeInTheDocument()
    expect(screen.getByText('Coloquio')).toBeInTheDocument()
    expect(screen.queryByText('mat-1')).not.toBeInTheDocument()
  })
})

describe('ConvocatoriaForm — crear convocatoria', () => {
  it('muestra selects de materia, cohorte y tipo (no inputs de texto libre)', async () => {
    mockGetByUrl({
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
      '/api/v1/admin/cohortes': COHORTES_FIXTURE,
    })

    renderWithProviders(<ConvocatoriaForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    expect((await screen.findByLabelText('Materia')).tagName).toBe('SELECT')
    expect(screen.getByLabelText('Cohorte').tagName).toBe('SELECT')
    expect(screen.getByLabelText('Tipo').tagName).toBe('SELECT')
    expect(await screen.findByRole('option', { name: 'Programación I' })).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: '2026' })).toBeInTheDocument()
  })

  it('bloquea envío sin completar los campos requeridos', async () => {
    mockGetByUrl({
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
      '/api/v1/admin/cohortes': COHORTES_FIXTURE,
    })

    const user = userEvent.setup()
    renderWithProviders(<ConvocatoriaForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    await screen.findByRole('option', { name: 'Programación I' })
    await user.click(screen.getByRole('button', { name: /Crear convocatoria/i }))

    expect(await screen.findByText('Seleccione una materia', { selector: 'p' })).toBeInTheDocument()
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })

  it('llama POST /api/coloquios con materia_id, cohorte_id, tipo y dias_disponibles numérico', async () => {
    mockGetByUrl({
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
      '/api/v1/admin/cohortes': COHORTES_FIXTURE,
    })
    mockApiClient.post.mockResolvedValueOnce({ data: { id: 'col-1' } })

    const user = userEvent.setup()
    renderWithProviders(<ConvocatoriaForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    await screen.findByRole('option', { name: 'Programación I' })
    await user.selectOptions(screen.getByLabelText('Materia'), 'mat-1')
    await user.selectOptions(screen.getByLabelText('Cohorte'), 'coh-1')
    await user.selectOptions(screen.getByLabelText('Tipo'), 'Coloquio')
    await user.type(screen.getByPlaceholderText(/Primer llamado/i), 'Primer llamado')
    await user.type(screen.getByLabelText(/Cantidad de días/i), '5')
    await user.type(screen.getByLabelText(/Cupo por día/i), '10')

    await user.click(screen.getByRole('button', { name: /Crear convocatoria/i }))

    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/api/coloquios',
      expect.objectContaining({
        materia_id: 'mat-1',
        cohorte_id: 'coh-1',
        tipo: 'Coloquio',
        instancia: 'Primer llamado',
        dias_disponibles: 5,
        cupo_por_dia: 10,
      }),
    )
  })
})

describe('EditarConvocatoriaForm — solo campos que el backend persiste', () => {
  it('precarga tipo, instancia y dias_disponibles, y los envía por PATCH', async () => {
    mockApiClient.patch.mockResolvedValueOnce({ data: { id: 'col-1' } })

    const user = userEvent.setup()
    renderWithProviders(
      <EditarConvocatoriaForm
        convocatoria={CONVOCATORIA_FIXTURE}
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
      />,
    )

    expect(screen.getByDisplayValue('Primer llamado')).toBeInTheDocument()
    expect(screen.getByDisplayValue('5')).toBeInTheDocument()

    await user.clear(screen.getByLabelText(/Cantidad de días/i))
    await user.type(screen.getByLabelText(/Cantidad de días/i), '8')
    await user.click(screen.getByRole('button', { name: /Actualizar convocatoria/i }))

    expect(mockApiClient.patch).toHaveBeenCalledWith(
      '/api/coloquios/col-1',
      expect.objectContaining({
        tipo: 'Coloquio',
        instancia: 'Primer llamado',
        dias_disponibles: 8,
      }),
    )
  })
})
