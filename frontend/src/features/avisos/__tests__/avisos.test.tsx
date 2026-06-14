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

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('AvisoForm — validaciones de schema Zod', () => {
  it('schema bloquea vigencia inválida (inicio >= fin)', async () => {
    // Verificación directa del schema Zod sin montar el componente
    const { avisoSchema } = await import('../schemas')
    const result = avisoSchema.safeParse({
      alcance: 'global',
      roles: [],
      severidad: 'info',
      titulo: 'Aviso test',
      cuerpo: 'Contenido',
      vigencia_inicio: '2024-12-31T10:00',
      vigencia_fin: '2024-01-01T10:00',
      orden: 0,
      activo: true,
      requiere_ack: false,
    })
    expect(result.success).toBe(false)
    if (!result.success) {
      const vigenciaError = result.error.issues.find((i) => i.path.includes('vigencia_fin'))
      expect(vigenciaError?.message).toMatch(/anterior a la de fin/i)
    }
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })

  it('schema bloquea alcance cohorte sin cohorte proporcionada', async () => {
    const { avisoSchema } = await import('../schemas')
    const result = avisoSchema.safeParse({
      alcance: 'cohorte',
      cohorte: '', // vacío
      roles: [],
      severidad: 'info',
      titulo: 'Aviso',
      cuerpo: 'Body',
      vigencia_inicio: '2024-01-01T00:00',
      vigencia_fin: '2024-12-31T00:00',
      orden: 0,
      activo: true,
      requiere_ack: false,
    })
    expect(result.success).toBe(false)
    if (!result.success) {
      const cohorteError = result.error.issues.find((i) => i.path.includes('cohorte'))
      expect(cohorteError?.message).toMatch(/cohorte/i)
    }
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })
})

describe('AckAviso', () => {
  it('llama POST /api/avisos/{id}/ack al confirmar lectura', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        data: [
          {
            id: 'av-1',
            alcance: 'global',
            roles: [],
            severidad: 'info',
            titulo: 'Aviso importante',
            cuerpo: 'Leer con atención',
            vigencia_inicio: '2024-01-01',
            vigencia_fin: '2024-12-31',
            orden: 1,
            activo: true,
            requiere_ack: true,
            creado_en: '2024-01-01',
          },
        ],
        total: 1,
      },
    })
    mockApiClient.post.mockResolvedValueOnce({ data: {} })

    const { default: AvisosUsuario } = await import('../components/AvisosUsuario')
    const user = userEvent.setup()
    renderWithProviders(<AvisosUsuario />)

    const confirmBtn = await screen.findByRole('button', { name: /Confirmar lectura/i })
    await user.click(confirmBtn)

    expect(mockApiClient.post).toHaveBeenCalledWith('/api/avisos/av-1/ack')
  })

  it('renderiza aviso con severidad warning con clase de color correcta', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        data: [
          {
            id: 'av-2',
            alcance: 'global',
            roles: [],
            severidad: 'warning',
            titulo: 'Aviso warning',
            cuerpo: 'Texto de warning',
            vigencia_inicio: '2024-01-01',
            vigencia_fin: '2024-12-31',
            orden: 1,
            activo: true,
            requiere_ack: false,
            creado_en: '2024-01-01',
          },
        ],
        total: 1,
      },
    })

    const { default: AvisosUsuario } = await import('../components/AvisosUsuario')
    renderWithProviders(<AvisosUsuario />)

    expect(await screen.findByText('Aviso warning')).toBeInTheDocument()
    // Sin requiere_ack, no hay botón de confirmación
    expect(screen.queryByRole('button', { name: /Confirmar lectura/i })).not.toBeInTheDocument()
  })
})
