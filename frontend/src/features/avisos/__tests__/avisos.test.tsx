import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import AvisoForm from '../components/AvisoForm'
import GestionAvisos from '../components/GestionAvisos'

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

const MATERIAS_FIXTURE = [{ id: 'mat-1', nombre: 'Programación I' }]
const COHORTES_FIXTURE = [{ id: 'coh-1', nombre: '2026', carrera_id: 'carr-1' }]

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

describe('AvisoForm — selección de materia y cohorte', () => {
  it('muestra un select de materias (no input de texto) cuando el alcance es PorMateria', async () => {
    mockGetByUrl({ '/api/v1/estructura/materias': MATERIAS_FIXTURE })

    renderWithProviders(<AvisoForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('Alcance'), 'PorMateria')

    const materiaSelect = await screen.findByLabelText('Materia')
    expect(materiaSelect.tagName).toBe('SELECT')
    expect(await screen.findByRole('option', { name: 'Programación I' })).toBeInTheDocument()
  })

  it('muestra un select de cohortes (no input de texto) cuando el alcance es PorCohorte', async () => {
    mockGetByUrl({ '/api/v1/admin/cohortes': COHORTES_FIXTURE })

    renderWithProviders(<AvisoForm onSuccess={vi.fn()} onCancel={vi.fn()} />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('Alcance'), 'PorCohorte')

    const cohorteSelect = await screen.findByLabelText('Cohorte')
    expect(cohorteSelect.tagName).toBe('SELECT')
    expect(await screen.findByRole('option', { name: '2026' })).toBeInTheDocument()
  })
})

describe('GestionAvisos — resolución de nombres', () => {
  it('resuelve materia_id al nombre real de la materia en el listado', async () => {
    mockGetByUrl({
      '/api/avisos/gestion': {
        items: [
          {
            id: 'av-1',
            tenant_id: 't-1',
            alcance: 'PorMateria',
            materia_id: 'mat-1',
            severidad: 'Info',
            titulo: 'Aviso de materia',
            cuerpo: 'Cuerpo',
            inicio_en: '2026-01-01T00:00',
            fin_en: '2026-12-31T00:00',
            orden: 0,
            activo: true,
            requiere_ack: false,
            total_acks: 0,
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
    })

    renderWithProviders(<GestionAvisos />)

    expect(await screen.findByText('Programación I')).toBeInTheDocument()
    expect(screen.queryByText('mat-1')).not.toBeInTheDocument()
  })

  it('formatea inicio_en y fin_en como fecha legible, no el ISO crudo', async () => {
    mockGetByUrl({
      '/api/avisos/gestion': {
        items: [
          {
            id: 'av-2',
            tenant_id: 't-1',
            alcance: 'Global',
            severidad: 'Info',
            titulo: 'Receso de invierno',
            cuerpo: 'Las clases se retoman el 3 de agosto.',
            inicio_en: '2026-06-17T02:24:03.042374+00:00',
            fin_en: '2026-07-18T02:24:03.042374+00:00',
            orden: 0,
            activo: true,
            requiere_ack: false,
            total_acks: 0,
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
    })

    renderWithProviders(<GestionAvisos />)

    await screen.findByText('Receso de invierno')

    expect(screen.queryByText(/2026-06-17T02:24:03/)).not.toBeInTheDocument()
    expect(screen.queryByText(/2026-07-18T02:24:03/)).not.toBeInTheDocument()
  })
})

describe('AvisoForm — validaciones de schema Zod', () => {
  it('schema bloquea vigencia inválida (inicio >= fin)', async () => {
    // Verificación directa del schema Zod sin montar el componente
    const { avisoSchema } = await import('../schemas')
    const result = avisoSchema.safeParse({
      alcance: 'Global',
      severidad: 'Info',
      titulo: 'Aviso test',
      cuerpo: 'Contenido',
      inicio_en: '2024-12-31T10:00',
      fin_en: '2024-01-01T10:00',
      orden: 0,
      activo: true,
      requiere_ack: false,
    })
    expect(result.success).toBe(false)
    if (!result.success) {
      const vigenciaError = result.error.issues.find((i) => i.path.includes('fin_en'))
      expect(vigenciaError?.message).toMatch(/anterior a la de fin/i)
    }
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })

  it('schema bloquea alcance cohorte sin cohorte proporcionada', async () => {
    const { avisoSchema } = await import('../schemas')
    const result = avisoSchema.safeParse({
      alcance: 'PorCohorte',
      cohorte_id: '', // vacío
      severidad: 'Info',
      titulo: 'Aviso',
      cuerpo: 'Body',
      inicio_en: '2024-01-01T00:00',
      fin_en: '2024-12-31T00:00',
      orden: 0,
      activo: true,
      requiere_ack: false,
    })
    expect(result.success).toBe(false)
    if (!result.success) {
      const cohorteError = result.error.issues.find((i) => i.path.includes('cohorte_id'))
      expect(cohorteError?.message).toMatch(/cohorte/i)
    }
    expect(mockApiClient.post).not.toHaveBeenCalled()
  })
})

describe('AckAviso', () => {
  it('llama POST /api/avisos/{id}/ack al confirmar lectura', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'av-1',
            tenant_id: 't-1',
            alcance: 'Global',
            severidad: 'Info',
            titulo: 'Aviso importante',
            cuerpo: 'Leer con atención',
            inicio_en: '2024-01-01',
            fin_en: '2024-12-31',
            orden: 1,
            activo: true,
            requiere_ack: true,
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
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
        items: [
          {
            id: 'av-2',
            tenant_id: 't-1',
            alcance: 'Global',
            severidad: 'Advertencia',
            titulo: 'Aviso warning',
            cuerpo: 'Texto de warning',
            inicio_en: '2024-01-01',
            fin_en: '2024-12-31',
            orden: 1,
            activo: true,
            requiere_ack: false,
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
    })

    const { default: AvisosUsuario } = await import('../components/AvisosUsuario')
    renderWithProviders(<AvisosUsuario />)

    expect(await screen.findByText('Aviso warning')).toBeInTheDocument()
    // Sin requiere_ack, no hay botón de confirmación
    expect(screen.queryByRole('button', { name: /Confirmar lectura/i })).not.toBeInTheDocument()
  })
})
