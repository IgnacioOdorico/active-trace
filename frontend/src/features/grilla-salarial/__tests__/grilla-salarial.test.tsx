import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import SalarioBaseABM from '../components/SalarioBaseABM'
import SalarioBaseForm from '../components/SalarioBaseForm'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    put: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

const salarioBase = {
  id: 'sb-1',
  rol: 'PROFESOR',
  monto: 80000,
  desde: '2024-01-01',
  hasta: null,
  activo: true,
}

// 9.3 — ABM grilla salarial
describe('SalarioBaseABM — listado', () => {
  it('muestra estado vacío cuando no hay salarios', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [] })
    renderWithProviders(<SalarioBaseABM />)
    expect(await screen.findByText(/No hay salarios base/i)).toBeInTheDocument()
  })

  it('renderiza filas con los salarios recibidos', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [salarioBase] })
    renderWithProviders(<SalarioBaseABM />)
    expect(await screen.findByText('PROFESOR')).toBeInTheDocument()
    expect(screen.getByText('Vigente')).toBeInTheDocument()
  })
})

describe('SalarioBaseForm — alta y validaciones', () => {
  it('alta válida llama POST e invalida query', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: salarioBase })
    const onSuccess = vi.fn()
    renderWithProviders(<SalarioBaseForm onSuccess={onSuccess} />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByRole('combobox'), 'PROFESOR')
    await user.type(screen.getByPlaceholderText('0.00'), '80000')
    await user.type(screen.getAllByDisplayValue('')[0], '2024-01-01')

    await user.click(screen.getByRole('button', { name: /Guardar salario base/i }))

    await waitFor(() => expect(mockApiClient.post).toHaveBeenCalledWith(
      '/api/salario-base',
      expect.objectContaining({ rol: 'PROFESOR', monto: 80000 }),
    ))
    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
  })

  it('validación de vigencia: desde >= hasta bloquea envío', async () => {
    const onSuccess = vi.fn()
    renderWithProviders(<SalarioBaseForm onSuccess={onSuccess} />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByRole('combobox'), 'PROFESOR')
    await user.type(screen.getByPlaceholderText('0.00'), '80000')

    // Ingresar desde > hasta
    const dateInputs = screen.getAllByDisplayValue('')
    await user.type(dateInputs[0], '2024-06-01')
    await user.type(dateInputs[1], '2024-01-01')

    await user.click(screen.getByRole('button', { name: /Guardar salario base/i }))

    await waitFor(() => {
      expect(screen.getByText(/anterior a/i)).toBeInTheDocument()
    })
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })

  it('maneja 409/422 de solapamiento sin perder el formulario', async () => {
    mockApiClient.post.mockRejectedValueOnce({
      response: {
        status: 409,
        data: { detail: 'SOLAPAMIENTO_VIGENCIA' },
      },
    })
    const onSuccess = vi.fn()
    renderWithProviders(<SalarioBaseForm onSuccess={onSuccess} />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByRole('combobox'), 'PROFESOR')
    await user.type(screen.getByPlaceholderText('0.00'), '80000')

    const dateInputs = screen.getAllByDisplayValue('')
    await user.type(dateInputs[0], '2024-01-01')

    await user.click(screen.getByRole('button', { name: /Guardar salario base/i }))

    await waitFor(() =>
      expect(screen.getByText(/Error del servidor/i)).toBeInTheDocument(),
    )
    // El formulario sigue visible (no desmontado)
    expect(screen.getByRole('button', { name: /Guardar salario base/i })).toBeInTheDocument()
    expect(onSuccess).not.toHaveBeenCalled()
  })
})
