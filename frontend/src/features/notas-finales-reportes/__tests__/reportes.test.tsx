import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../../academico/hooks/useMaterias', () => ({
  useMaterias: vi.fn().mockReturnValue({
    data: [{ id: 'm-1', nombre: 'Programación I' }],
    isLoading: false,
  }),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => vi.fn() }
})

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

// nota_final puede venir null cuando el alumno no tiene nota numérica para
// la actividad seleccionada (ej. celda vacía en el csv importado) — esto
// rompía con "Cannot read properties of null (reading 'toFixed')".
describe('ReportesPage — nota_final nula', () => {
  it('muestra "—" en vez de crashear cuando nota_final es null', async () => {
    mockApiClient.get.mockImplementation((url: string) => {
      if (url.includes('/actividades')) {
        return Promise.resolve({ data: [{ id: 'Segundo Parcial (Real)', nombre: 'Segundo Parcial (Real)', tipo: 'numerica' }] })
      }
      return Promise.resolve({
        data: {
          total_alumnos: 12, total_actividades: 3, total_calificaciones: 36,
          promedio_aprobacion_general: 70, alumnos_atrasados_count: 2,
          alumnos_aprobados_count: 10, sin_datos: false,
        },
      })
    })
    mockApiClient.post.mockResolvedValueOnce({
      data: [
        {
          nombre: 'Agustina', apellidos: 'Álvarez', comision: 'B',
          nota_final: null, actividades_textuales: [], estado: 'no_aprobado',
        },
        {
          nombre: 'Lautaro', apellidos: 'Martínez', comision: 'A',
          nota_final: 85.5, actividades_textuales: [], estado: 'aprobado',
        },
      ],
    })

    const { default: ReportesPage } = await import('../pages/ReportesPage')
    const user = userEvent.setup()
    renderWithProviders(<ReportesPage />)

    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    const pill = await screen.findByRole('button', { name: /Segundo Parcial \(Real\)/i })
    await user.click(pill)
    await user.click(screen.getByRole('button', { name: /Calcular Nota Final/i }))

    expect(await screen.findByText('—')).toBeInTheDocument()
    expect(screen.getByText('85.5')).toBeInTheDocument()
  })
})
