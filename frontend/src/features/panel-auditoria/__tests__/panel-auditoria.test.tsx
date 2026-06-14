import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import AccionesPorDia from '../components/AccionesPorDia'
import FiltrosPanel from '../components/FiltrosPanel'
import UltimasAcciones from '../components/UltimasAcciones'

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
