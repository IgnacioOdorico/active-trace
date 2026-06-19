import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import AccionesPorDia from '../components/AccionesPorDia'
import FiltrosPanel from '../components/FiltrosPanel'
import UltimasAcciones from '../components/UltimasAcciones'
import ComunicacionesPorDocente from '../components/ComunicacionesPorDocente'
import InteraccionesDocenteMateria from '../components/InteraccionesDocenteMateria'

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
    data: [{ id: 'm-1', nombre: 'Matemática I', codigo: 'MAT1' }],
  }),
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

// 9.4 — Panel de auditoría con filtros
describe('AccionesPorDia — sub-vista', () => {
  it('muestra estado vacío cuando no hay datos', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [] })
    renderWithProviders(<AccionesPorDia filters={{}} />)
    expect(await screen.findByText(/sin acciones registradas/i)).toBeInTheDocument()
  })

  it('renderiza datos de la serie temporal', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: [
        { fecha: '2024-06-01', total: 15 },
        { fecha: '2024-06-02', total: 22 },
      ],
    })
    renderWithProviders(<AccionesPorDia filters={{}} />)
    expect(await screen.findByText('15')).toBeInTheDocument()
    expect(screen.getByText('22')).toBeInTheDocument()
  })

  it('propaga filtro de materia al endpoint', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [] })
    renderWithProviders(<AccionesPorDia filters={{ materia_id: 'm-1' }} />)
    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('materia_id=m-1'),
      )
    })
  })
})

describe('FiltrosPanel — propagación de filtros', () => {
  it('actualiza filtros al cambiar materia', async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <FiltrosPanel filters={{}} onChange={onChange} />,
    )

    const select = screen.getByRole('combobox')
    await userEvent.setup().selectOptions(select, 'm-1')

    await waitFor(() =>
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({ materia_id: 'm-1' }),
      ),
    )
  })

  it('actualiza filtro de acción al escribir', async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <FiltrosPanel filters={{}} onChange={onChange} />,
    )

    const input = screen.getByPlaceholderText(/Ej: LIQUIDACION_CERRAR/i)
    await userEvent.setup().type(input, 'LIQUIDACION_CALCULAR')

    await waitFor(() =>
      expect(onChange).toHaveBeenLastCalledWith(
        expect.objectContaining({ accion: expect.stringContaining('LIQUIDACION_CALCULAR') }),
      ),
    )
  })
})

describe('UltimasAcciones — estado vacío', () => {
  it('muestra estado vacío cuando no hay acciones', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: { items: [], max_resultados: 200 } })
    renderWithProviders(<UltimasAcciones filters={{}} />)
    expect(await screen.findByText(/sin acciones en el rango/i)).toBeInTheDocument()
  })
})

describe('UltimasAcciones — nombres resueltos', () => {
  it('muestra actor_nombre y materia_nombre en vez del UUID crudo', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'log-1',
            fecha_hora: '2026-06-18T10:00:00Z',
            actor_id: '43330de7-02c7-4277-a07a-f5b86d5c26fc',
            actor_nombre: 'Ana García',
            impersonado_id: null,
            materia_id: '42fa9519-1111-2222-3333-444455556666',
            materia_nombre: 'Matemática I',
            accion: 'COLOQUIO_CREAR',
            detalle: null,
            filas_afectadas: 1,
            ip: null,
            user_agent: null,
          },
        ],
        max_resultados: 200,
      },
    })
    renderWithProviders(<UltimasAcciones filters={{}} />)
    expect(await screen.findByText('Ana García')).toBeInTheDocument()
    expect(screen.getByText('Matemática I')).toBeInTheDocument()
    expect(screen.queryByText(/43330de7/)).not.toBeInTheDocument()
  })

  it('si actor_nombre viene vacío, cae al UUID truncado como fallback', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'log-2',
            fecha_hora: '2026-06-18T10:00:00Z',
            actor_id: '43330de7-02c7-4277-a07a-f5b86d5c26fc',
            actor_nombre: '',
            impersonado_id: null,
            materia_id: null,
            materia_nombre: null,
            accion: 'COLOQUIO_CREAR',
            detalle: null,
            filas_afectadas: 1,
            ip: null,
            user_agent: null,
          },
        ],
        max_resultados: 200,
      },
    })
    renderWithProviders(<UltimasAcciones filters={{}} />)
    expect(await screen.findByText(/43330de7/)).toBeInTheDocument()
  })
})

// Contrato real: docente_id/docente_nombre (no actor_id/actor_nombre)
describe('ComunicacionesPorDocente — contrato real del backend', () => {
  it('renderiza filas usando docente_id/docente_nombre', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: [
        {
          docente_id: 'd-1',
          docente_nombre: 'Ana García',
          pendiente: 1,
          enviando: 0,
          enviado: 3,
          fallido: 0,
          cancelado: 0,
        },
      ],
    })
    renderWithProviders(<ComunicacionesPorDocente filters={{}} />)
    expect(await screen.findByText('Ana García')).toBeInTheDocument()
  })
})

// Contrato real: docente_id/docente_nombre/total_acciones/acciones_por_tipo
describe('InteraccionesDocenteMateria — contrato real del backend', () => {
  it('renderiza filas y desglose por tipo sin romper', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: [
        {
          docente_id: 'd-1',
          docente_nombre: 'Ana García',
          materia_id: 'm-1',
          materia_nombre: 'Matemática I',
          total_acciones: 5,
          acciones_por_tipo: { EVALUACION_CREAR: 3, EVALUACION_EDITAR: 2 },
        },
      ],
    })
    renderWithProviders(<InteraccionesDocenteMateria filters={{}} />)
    expect(await screen.findByText('Ana García')).toBeInTheDocument()
    expect(screen.getByText('Matemática I')).toBeInTheDocument()
    expect(screen.getByText('EVALUACION_CREAR: 3')).toBeInTheDocument()
  })

  it('no rompe si acciones_por_tipo viene vacío/ausente', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: [
        {
          docente_id: 'd-1',
          docente_nombre: 'Ana García',
          materia_id: 'm-1',
          materia_nombre: 'Matemática I',
          total_acciones: 0,
          acciones_por_tipo: undefined,
        },
      ],
    })
    renderWithProviders(<InteraccionesDocenteMateria filters={{}} />)
    expect(await screen.findByText('Ana García')).toBeInTheDocument()
  })
})
