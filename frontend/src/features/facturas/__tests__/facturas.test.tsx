import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import CargarFacturaForm from '../components/CargarFacturaForm'
import FacturasListado from '../components/FacturasListado'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

const facturaPendiente = {
  id: 'f-1',
  usuario_id: 'u-1',
  periodo: '2024-06',
  detalle: 'Comprobante junio',
  referencia_archivo: '/data/f-1.pdf',
  tamano_kb: 512,
  estado: 'Pendiente' as const,
  cargada_at: '2024-06-15T10:00:00Z',
  abonada_at: null,
}

// 9.5 — Carga de factura: validación PDF y cambio de estado
describe('CargarFacturaForm — validación de PDF', () => {
  it('bloquea envío si el archivo no es PDF', async () => {
    const onSuccess = vi.fn()
    renderWithProviders(<CargarFacturaForm onSuccess={onSuccess} />)

    const user = userEvent.setup({ applyAccept: false })
    await user.type(screen.getByPlaceholderText(/Describí el comprobante/i), 'Comprobante')

    const file = new File(['content'], 'documento.docx', { type: 'application/msword' })
    const fileInput = screen.getByLabelText(/Archivo PDF/i)
    await user.upload(fileInput, file)

    await user.click(screen.getByRole('button', { name: /Cargar factura/i }))

    await waitFor(() => {
      expect(screen.getByText(/debe ser un PDF/i)).toBeInTheDocument()
    })
    expect(mockApiClient.post).not.toHaveBeenCalled()
    expect(onSuccess).not.toHaveBeenCalled()
  })

  it('envía multipart/form-data con PDF válido y llama onSuccess', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: facturaPendiente })
    const onSuccess = vi.fn()
    renderWithProviders(<CargarFacturaForm onSuccess={onSuccess} />)

    const user = userEvent.setup()

    const periodoInput = screen.getAllByRole('textbox').find((_) => true)!
    // Se interactúa con el input de mes (month input)
    const monthInput = screen.getByLabelText(/Período/i)
    await user.click(monthInput)

    const detalleInput = screen.getByPlaceholderText(/Describí el comprobante/i)
    await user.type(detalleInput, 'Mi factura')

    const file = new File(['%PDF-1.4'], 'factura.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByLabelText(/Archivo PDF/i)
    await user.upload(fileInput, file)

    await user.click(screen.getByRole('button', { name: /Cargar factura/i }))

    // Al ser período vacío, no debe enviar
    await waitFor(() => {
      expect(screen.getByText(/período es requerido/i)).toBeInTheDocument()
    })
    expect(onSuccess).not.toHaveBeenCalled()
  })
})

describe('FacturasListado — cambio de estado a Abonada', () => {
  it('muestra listado con factura pendiente y botón Marcar abonada', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [facturaPendiente] })
    renderWithProviders(<FacturasListado puedeAbonar={true} />)

    expect(await screen.findByText('Comprobante junio')).toBeInTheDocument()
    expect(within(screen.getByRole('table')).getByText('Pendiente')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Marcar abonada/i })).toBeInTheDocument()
  })

  it('llama PATCH /abonar al marcar como abonada', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [facturaPendiente] })
    mockApiClient.patch.mockResolvedValueOnce({
      data: { id: 'f-1', estado: 'Abonada', abonada_at: '2024-06-20T12:00:00Z' },
    })

    renderWithProviders(<FacturasListado puedeAbonar={true} />)

    await screen.findByText('Comprobante junio')
    await userEvent.setup().click(screen.getByRole('button', { name: /Marcar abonada/i }))

    await waitFor(() =>
      expect(mockApiClient.patch).toHaveBeenCalledWith('/api/facturas/f-1/abonar'),
    )
  })

  it('maneja 409 (ya abonada) con mensaje no destructivo', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [facturaPendiente] })
    mockApiClient.patch.mockRejectedValueOnce({
      response: { status: 409, data: { detail: 'FACTURA_YA_ABONADA' } },
    })

    renderWithProviders(<FacturasListado puedeAbonar={true} />)

    await screen.findByText('Comprobante junio')
    await userEvent.setup().click(screen.getByRole('button', { name: /Marcar abonada/i }))

    await waitFor(() =>
      expect(screen.getByText(/ya estaba marcada como abonada/i)).toBeInTheDocument(),
    )
  })

  it('oculta botón Marcar abonada si no tiene permiso', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: [facturaPendiente] })
    renderWithProviders(<FacturasListado puedeAbonar={false} />)

    await screen.findByText('Comprobante junio')
    expect(screen.queryByRole('button', { name: /Marcar abonada/i })).not.toBeInTheDocument()
  })
})
